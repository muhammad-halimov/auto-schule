<?php

namespace App\Controller\Api\Progress;

use App\Entity\User;
use Doctrine\Common\Collections\ArrayCollection;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Bundle\SecurityBundle\Security;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Throwable;

#[Route('/api/progress', name: 'api_progress', methods: ['GET'])]
class ProgressController extends AbstractController
{
    public function __construct(
        private readonly Security $security
    ) {}

    #[Route('', name: 'api_progress_get', methods: ['GET'])]
    public function getProgress(): JsonResponse
    {
        $this->denyAccessUnlessGranted('IS_AUTHENTICATED_FULLY');

        try {
            /** @var User $user */
            $user = $this->security->getUser();

            // 1. Получаем данные с защитой от ошибок
            $lessonProgress = method_exists($user, 'getProgress')
                ? ($user->getProgress() ?? ['byCourse' => [], 'overall' => []])
                : ['byCourse' => [], 'overall' => []];

            $quizProgress = method_exists($user, 'getQuizProgressStats')
                ? ($user->getQuizProgressStats() ?? ['progress' => ['byCourse' => [], 'overall' => []], 'completed' => []])
                : ['progress' => ['byCourse' => [], 'overall' => []], 'completed' => []];

            // 2. Форматируем ответ
            $response = [
                'lessons' => [
                    'progress' => $lessonProgress,
                    'completed' => $this->getCompletedLessons($user)
                ],
                'quizzes' => [
                    'progress' => $quizProgress['progress'] ?? ['byCourse' => [], 'overall' => []],
                    'completed' => $quizProgress['completed'] ?? []
                ],
                'combinedProgress' => $this->calculateCombinedProgress(
                    $lessonProgress['byCourse'],
                    $quizProgress['progress']['byCourse'] ?? []
                )
            ];

            return $this->json($response);

        } catch (Throwable $e) {
            return $this->json([
                'error' => 'Failed to get progress data',
                'details' => $e->getMessage()
            ], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }

    private function getCompletedLessons(User $user): array
    {
        if (!method_exists($user, 'getLessonProgresses')) {
            return [];
        }

        $progresses = $user->getLessonProgresses() ?? new ArrayCollection();

        return $progresses->filter(fn($p) => $p !== null && $p->isCompleted())
            ->map(fn($p) => [
                'lessonId' => $p->getLesson()?->getId(),
                'title' => $p->getLesson()?->getTitle() ?? 'Unknown',
                'courseId' => $p->getLesson()?->getCourse()?->getId(),
                'completedAt' => $p->getCompletedAt()?->format('Y-m-d H:i:s')
            ])
            ->toArray();
    }

    private function calculateCombinedProgress(array $lessons, array $quizzes): array
    {
        $courses = [];

        // Сначала собираем данные по урокам
        foreach ($lessons as $lesson) {
            if (!is_array($lesson)) {
                continue;
            }
            $courseId = $lesson['courseId'];
            if (!isset($courses[$courseId])) {
                $courses[$courseId] = [
                    'courseId' => $courseId,
                    'courseTitle' => $lesson['courseTitle'] ?? 'Unknown',
                    'lessonsCompleted' => 0,
                    'lessonsTotal' => 0,
                    'quizzesCompleted' => 0,
                    'quizzesTotal' => 0,
                    'correctAnswers' => 0,
                    'totalQuestions' => 0,
                ];
            }
            $courses[$courseId]['lessonsCompleted'] += $lesson['completed'] ?? 0;
            $courses[$courseId]['lessonsTotal'] += $lesson['total'] ?? 0;
        }

        // Затем по тестам
        foreach ($quizzes as $quiz) {
            if (!is_array($quiz)) {
                continue;
            }
            $courseId = $quiz['courseId'];
            if (!isset($courses[$courseId])) {
                $courses[$courseId] = [
                    'courseId' => $courseId,
                    'courseTitle' => $quiz['courseTitle'] ?? 'Unknown',
                    'lessonsCompleted' => 0,
                    'lessonsTotal' => 0,
                    'quizzesCompleted' => 0,
                    'quizzesTotal' => 0,
                    'correctAnswers' => 0,
                    'totalQuestions' => 0,
                ];
            }
            $courses[$courseId]['quizzesCompleted'] += $quiz['completed'] ?? 0;
            $courses[$courseId]['quizzesTotal'] += $quiz['total'] ?? 0;
            $courses[$courseId]['correctAnswers'] += $quiz['details']['correctAnswers'] ?? 0;
            $courses[$courseId]['totalQuestions'] += $quiz['details']['totalQuestions'] ?? 0;
        }

        $result = ['byCourse' => [], 'overall' => [
            'percentage' => 0,
        ]];

        foreach ($courses as $course) {
            // Считаем уроки
            $lessonPercentage = $course['lessonsTotal'] > 0
                ? round(($course['lessonsCompleted'] / $course['lessonsTotal']) * 100)
                : 0;

            // Считаем тесты по формуле correctAnswers / totalQuestions
            $quizPercentage = $course['totalQuestions'] > 0
                ? round(($course['correctAnswers'] / $course['totalQuestions']) * 100)
                : 0;

            // Итог — среднее арифметическое процентов уроков и тестов
            $combinedPercentage = round(($lessonPercentage + $quizPercentage) / 2);

            $result['byCourse'][] = [
                'courseId' => $course['courseId'],
                'courseTitle' => $course['courseTitle'],
                'details' => [
                    'lessons' => [
                        'completed' => $course['lessonsCompleted'],
                        'total' => $course['lessonsTotal'],
                        'percentage' => $lessonPercentage,
                    ],
                    'quizzes' => [
                        'completed' => $course['quizzesCompleted'],
                        'total' => $course['quizzesTotal'],
                        'correctAnswers' => $course['correctAnswers'],
                        'totalQuestions' => $course['totalQuestions'],
                        'correctPercentage' => $quizPercentage,
                    ],
                ],
                'percentage' => $combinedPercentage,
            ];
        }

        // Можно добавить общий процент, если нужно
        // По аналогии — среднее по всем курсам или просто по суммарным данным

        return $result;
    }
}

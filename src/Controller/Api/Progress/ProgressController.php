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

        // Обрабатываем уроки
        foreach ($lessons as $lesson) {
            if (!is_array($lesson)) {
                continue;
            }
            $courseId = $lesson['courseId'];
            if (!isset($courses[$courseId])) {
                $courses[$courseId] = [
                    'courseId' => $courseId,
                    'courseTitle' => $lesson['courseTitle'] ?? 'Unknown',
                    'lessonsCompleted' => $lesson['completed'] ?? 0,
                    'lessonsTotal' => $lesson['total'] ?? 0,
                    'quizzesCompleted' => 0,
                    'quizzesTotal' => 0,
                    'correctAnswers' => 0,
                    'totalQuestions' => 0,
                ];
            } else {
                $courses[$courseId]['lessonsCompleted'] += $lesson['completed'] ?? 0;
                $courses[$courseId]['lessonsTotal'] += $lesson['total'] ?? 0;
            }
        }

        // Обрабатываем тесты
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
                    'quizzesCompleted' => $quiz['completed'] ?? 0,
                    'quizzesTotal' => $quiz['total'] ?? 0,
                    'correctAnswers' => $quiz['details']['correctAnswers'] ?? 0,
                    'totalQuestions' => $quiz['details']['totalQuestions'] ?? 0,
                ];
            } else {
                $courses[$courseId]['quizzesCompleted'] += $quiz['completed'] ?? 0;
                $courses[$courseId]['quizzesTotal'] += $quiz['total'] ?? 0;
                $courses[$courseId]['correctAnswers'] += $quiz['details']['correctAnswers'] ?? 0;
                $courses[$courseId]['totalQuestions'] += $quiz['details']['totalQuestions'] ?? 0;
            }
        }

        $result = [
            'byCourse' => [],
            'overall' => [
                'lessonsPercentageSum' => 0,
                'quizzesPercentageSum' => 0,
                'coursesCount' => 0,
            ]
        ];

        foreach ($courses as $course) {
            $lessonPercentage = ($course['lessonsTotal'] > 0)
                ? round(($course['lessonsCompleted'] / $course['lessonsTotal']) * 100)
                : 0;

            // Важно: correctPercentage = correctAnswers / quizzesTotal * 100
            $quizPercentage = ($course['quizzesTotal'] > 0)
                ? round(($course['correctAnswers'] / $course['quizzesTotal']) * 100)
                : 0;

            // Итог — среднее арифметическое уроков и тестов
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

            $result['overall']['lessonsPercentageSum'] += $lessonPercentage;
            $result['overall']['quizzesPercentageSum'] += $quizPercentage;
            $result['overall']['coursesCount']++;
        }

        if ($result['overall']['coursesCount'] > 0) {
            $result['overall']['percentage'] = round(
                (
                    $result['overall']['lessonsPercentageSum'] + $result['overall']['quizzesPercentageSum']
                ) / ($result['overall']['coursesCount'] * 2)
            );
        } else {
            $result['overall']['percentage'] = 0;
        }

        // Убираем временные поля из итогового результата
        unset(
            $result['overall']['lessonsPercentageSum'],
            $result['overall']['quizzesPercentageSum'],
            $result['overall']['coursesCount']
        );

        return $result;
    }
}

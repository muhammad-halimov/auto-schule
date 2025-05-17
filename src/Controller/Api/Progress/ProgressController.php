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

        // 1. Собираем данные по урокам
        foreach ($lessons as $lesson) {
            if (!isset($lesson['courseId'])) {
                continue;
            }

            $courses[$lesson['courseId']] = [
                'courseId' => $lesson['courseId'],
                'courseTitle' => $lesson['courseTitle'] ?? 'Unknown Course',
                'lessonsCompleted' => $lesson['completed'] ?? 0,
                'lessonsTotal' => $lesson['total'] ?? 0,
                'quizzesCompleted' => 0,
                'quizzesTotal' => 0,
                'correctAnswers' => 0,
                'totalQuestions' => 0
            ];
        }

        // 2. Добавляем данные по тестам
        foreach ($quizzes as $quiz) {
            if (!isset($quiz['courseId'])) {
                continue;
            }

            $courseId = $quiz['courseId'];
            if (!isset($courses[$courseId])) {
                $courses[$courseId] = [
                    'courseId' => $courseId,
                    'courseTitle' => $quiz['courseTitle'] ?? 'Unknown Course',
                    'lessonsCompleted' => 0,
                    'lessonsTotal' => 0,
                    'quizzesCompleted' => $quiz['completed'] ?? 0,
                    'quizzesTotal' => $quiz['total'] ?? 0,
                    'correctAnswers' => $quiz['details']['correctAnswers'] ?? 0,
                    'totalQuestions' => $quiz['details']['totalQuestions'] ?? 0
                ];
            } else {
                $courses[$courseId]['quizzesCompleted'] = $quiz['completed'] ?? 0;
                $courses[$courseId]['quizzesTotal'] = $quiz['total'] ?? 0;
                $courses[$courseId]['correctAnswers'] = $quiz['details']['correctAnswers'] ?? 0;
                $courses[$courseId]['totalQuestions'] = $quiz['details']['totalQuestions'] ?? 0;
            }
        }

        $result = [
            'byCourse' => [],
            'overall' => [
                'completed' => 0,
                'total' => 0,
                'percentage' => 0,
                'correctAnswers' => 0,
                'totalQuestions' => 0,
                'correctPercentage' => 0,
                'averagePercentage' => 0
            ]
        ];

        // 3. Рассчитываем проценты для каждого курса
        foreach ($courses as $course) {
            // Общее количество элементов (уроки + тесты)
            $totalElements = ($course['lessonsTotal'] > 0 ? 1 : 0) + ($course['quizzesTotal'] > 0 ? 1 : 0);

            // Процент по урокам
            $lessonPercentage = $course['lessonsTotal'] > 0
                ? ($course['lessonsCompleted'] / $course['lessonsTotal']) * 100
                : 0;

            // Процент по тестам
            $quizPercentage = $course['quizzesTotal'] > 0
                ? ($course['quizzesCompleted'] / $course['quizzesTotal']) * 100
                : 0;

            // Общий процент по курсу
            $coursePercentage = $totalElements > 0
                ? ($lessonPercentage + $quizPercentage) / $totalElements
                : 0;

            $result['byCourse'][] = [
                'courseId' => $course['courseId'],
                'courseTitle' => $course['courseTitle'],
                'completed' => $course['lessonsCompleted'] + $course['quizzesCompleted'],
                'total' => $course['lessonsTotal'] + $course['quizzesTotal'],
                'percentage' => round($coursePercentage),
                'details' => [
                    'lessons' => [
                        'completed' => $course['lessonsCompleted'],
                        'total' => $course['lessonsTotal'],
                        'percentage' => round($lessonPercentage)
                    ],
                    'quizzes' => [
                        'completed' => $course['quizzesCompleted'],
                        'total' => $course['quizzesTotal'],
                        'correctAnswers' => $course['correctAnswers'],
                        'totalQuestions' => $course['totalQuestions'],
                        'correctPercentage' => $course['totalQuestions'] > 0
                            ? round(($course['correctAnswers'] / $course['totalQuestions']) * 100)
                            : 0,
                        'averagePercentage' => $course['quizzesTotal'] > 0
                            ? round(($course['quizzesCompleted'] / $course['quizzesTotal']) * 100)
                            : 0
                    ]
                ]
            ];

            // Считаем общую статистику
            $result['overall']['completed'] += $course['lessonsCompleted'] + $course['quizzesCompleted'];
            $result['overall']['total'] += $course['lessonsTotal'] + $course['quizzesTotal'];
            $result['overall']['correctAnswers'] += $course['correctAnswers'];
            $result['overall']['totalQuestions'] += $course['totalQuestions'];
        }

        // 4. Рассчитываем общие проценты
        if ($result['overall']['total'] > 0) {
            $totalLessonElements = array_sum(array_column($courses, 'lessonsTotal'));
            $totalQuizElements = array_sum(array_column($courses, 'quizzesTotal'));
            $totalElements = ($totalLessonElements > 0 ? 1 : 0) + ($totalQuizElements > 0 ? 1 : 0);

            $overallLessonPercentage = $totalLessonElements > 0
                ? (array_sum(array_column($courses, 'lessonsCompleted')) / $totalLessonElements * 100)
                : 0;

            $overallQuizPercentage = $totalQuizElements > 0
                ? (array_sum(array_column($courses, 'quizzesCompleted')) / $totalQuizElements * 100)
                : 0;

            $result['overall']['percentage'] = $totalElements > 0
                ? round(($overallLessonPercentage + $overallQuizPercentage) / $totalElements)
                : 0;

            $result['overall']['correctPercentage'] = $result['overall']['totalQuestions'] > 0
                ? round(($result['overall']['correctAnswers'] / $result['overall']['totalQuestions']) * 100)
                : 0;

            $totalQuizzes = array_sum(array_column($courses, 'quizzesTotal'));
            $completedQuizzes = array_sum(array_column($courses, 'quizzesCompleted'));

            $result['overall']['averagePercentage'] = $totalQuizzes > 0
                ? round(($completedQuizzes / $totalQuizzes) * 100)
                : 0;
        }

        return $result;
    }
}

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

        // Обработка уроков
        foreach ($lessons as $lesson) {
            if (!is_array($lesson)) continue;
            $courses[$lesson['courseId']] = [
                'courseId' => $lesson['courseId'],
                'courseTitle' => $lesson['courseTitle'] ?? 'Unknown',
                'lessons' => [
                    'completed' => $lesson['completed'] ?? 0,
                    'total' => $lesson['total'] ?? 0,
                    'percentage' => $lesson['percentage'] ?? 0
                ],
                'quizzes' => [
                    'completed' => 0,
                    'total' => 0,
                    'correctAnswers' => 0,
                    'totalQuestions' => 0,
                    'percentage' => 0
                ]
            ];
        }

        // Обработка тестов
        foreach ($quizzes as $quiz) {
            if (!is_array($quiz)) continue;
            $courseId = $quiz['courseId'];

            if (!isset($courses[$courseId])) {
                $courses[$courseId] = [
                    'courseId' => $courseId,
                    'courseTitle' => $quiz['courseTitle'] ?? 'Unknown',
                    'lessons' => [
                        'completed' => 0,
                        'total' => 0,
                        'percentage' => 0
                    ],
                    'quizzes' => [
                        'completed' => $quiz['completed'] ?? 0,
                        'total' => $quiz['total'] ?? 0,
                        'correctAnswers' => $quiz['correctAnswers'] ?? 0,
                        'totalQuestions' => $quiz['totalQuestions'] ?? 0,
                        'percentage' => $quiz['percentage'] ?? 0
                    ]
                ];
            } else {
                $courses[$courseId]['quizzes']['completed'] += $quiz['completed'] ?? 0;
                $courses[$courseId]['quizzes']['total'] += $quiz['total'] ?? 0;
                $courses[$courseId]['quizzes']['correctAnswers'] += $quiz['correctAnswers'] ?? 0;
                $courses[$courseId]['quizzes']['totalQuestions'] += $quiz['totalQuestions'] ?? 0;

                // Пересчитываем процент правильных ответов для тестов
                if ($courses[$courseId]['quizzes']['totalQuestions'] > 0) {
                    $courses[$courseId]['quizzes']['percentage'] = round(
                        ($courses[$courseId]['quizzes']['correctAnswers'] / $courses[$courseId]['quizzes']['totalQuestions']) * 100
                    );
                }
            }
        }

        $result = ['byCourse' => [], 'overall' => [
            'completed' => 0,
            'total' => 0,
            'percentage' => 0,
            'correctAnswers' => 0,
            'totalQuestions' => 0,
            'correctPercentage' => 0
        ]];

        foreach ($courses as $course) {
            $completed = $course['lessons']['completed'] + $course['quizzes']['completed'];
            $total = $course['lessons']['total'] + $course['quizzes']['total'];

            // Рассчитываем общий процент для курса
            $percentage = 0;
            $countComponents = 0;

            if ($course['lessons']['total'] > 0) {
                $percentage += $course['lessons']['percentage'];
                $countComponents++;
            }

            if ($course['quizzes']['total'] > 0) {
                $percentage += $course['quizzes']['percentage'];
                $countComponents++;
            }

            $percentage = $countComponents > 0 ? round($percentage / $countComponents) : 0;

            $result['byCourse'][] = [
                'courseId' => $course['courseId'],
                'courseTitle' => $course['courseTitle'],
                'completed' => $completed,
                'total' => $total,
                'percentage' => $percentage,
                'details' => [
                    'lessons' => $course['lessons'],
                    'quizzes' => $course['quizzes']
                ]
            ];

            $result['overall']['completed'] += $completed;
            $result['overall']['total'] += $total;
            $result['overall']['correctAnswers'] += $course['quizzes']['correctAnswers'];
            $result['overall']['totalQuestions'] += $course['quizzes']['totalQuestions'];
        }

        // Общий процент завершенности
        if ($result['overall']['total'] > 0) {
            $result['overall']['percentage'] = round(
                ($result['overall']['completed'] / $result['overall']['total']) * 100
            );
        }

        // Общий процент правильных ответов
        if ($result['overall']['totalQuestions'] > 0) {
            $result['overall']['correctPercentage'] = round(
                ($result['overall']['correctAnswers'] / $result['overall']['totalQuestions']) * 100
            );
        }

        return $result;
    }
}

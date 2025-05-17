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
            if (!is_array($lesson)) {
                continue;
            }
            $courses[$lesson['courseId']] = [
                'courseId' => $lesson['courseId'],
                'courseTitle' => $lesson['courseTitle'] ?? 'Unknown',
                'lessonsCompleted' => $lesson['completed'] ?? 0,
                'lessonsTotal' => $lesson['total'] ?? 0,
                'quizzesCompleted' => 0,
                'quizzesTotal' => 0,
                'correctAnswers' => 0,
                'totalQuestions' => 0
            ];
        }

        // Обработка тестов
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
                    'totalQuestions' => $quiz['details']['totalQuestions'] ?? 0
                ];
            } else {
                $courses[$courseId]['quizzesCompleted'] = $quiz['completed'] ?? 0;
                $courses[$courseId]['quizzesTotal'] = $quiz['total'] ?? 0;
                $courses[$courseId]['correctAnswers'] = $quiz['details']['correctAnswers'] ?? 0;
                $courses[$courseId]['totalQuestions'] = $quiz['details']['totalQuestions'] ?? 0;
            }
        }

        $result = ['byCourse' => [], 'overall' => [
            'completed' => 0,
            'total' => 0,
            'percentage' => 0,
            'correctAnswers' => 0,
            'totalQuestions' => 0,
            'correctPercentage' => 0,
            'averagePercentage' => 0
        ]];

        foreach ($courses as $course) {
            // Считаем проценты по урокам и тестам
            $lessonPercentage = $course['lessonsTotal'] > 0
                ? ($course['lessonsCompleted'] / $course['lessonsTotal']) * 100
                : 0;

            $quizPercentage = $course['quizzesTotal'] > 0
                ? ($course['quizzesCompleted'] / $course['quizzesTotal']) * 100
                : 0;

            // Средний процент по курсу
            $percentage = round(($lessonPercentage + $quizPercentage) / 2);

            $quizCorrectPercentage = $course['totalQuestions'] > 0
                ? round(($course['correctAnswers'] / $course['totalQuestions']) * 100, 1)
                : 0;

            $averageCorrectPercentage = $course['quizzesCompleted'] > 0
                ? round($course['correctAnswers'] / $course['quizzesCompleted'] * 100, 1)
                : 0;

            $result['byCourse'][] = [
                'courseId' => $course['courseId'],
                'courseTitle' => $course['courseTitle'],
                'completed' => $course['lessonsCompleted'] + $course['quizzesCompleted'],
                'total' => $course['lessonsTotal'] + $course['quizzesTotal'],
                'percentage' => $percentage,
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
                        'correctPercentage' => $quizCorrectPercentage,
                        'averagePercentage' => $averageCorrectPercentage
                    ]
                ]
            ];

            $result['overall']['completed'] += $course['lessonsCompleted'] + $course['quizzesCompleted'];
            $result['overall']['total'] += $course['lessonsTotal'] + $course['quizzesTotal'];
            $result['overall']['correctAnswers'] += $course['correctAnswers'];
            $result['overall']['totalQuestions'] += $course['totalQuestions'];
        }

        // Общий процент по всем курсам — среднее значение процентов по каждому курсу
        $totalCourses = count($result['byCourse']);
        $sumPercentage = array_reduce($result['byCourse'], function ($carry, $course) {
            return $carry + $course['percentage'];
        }, 0);

        $result['overall']['percentage'] = $totalCourses > 0
            ? round($sumPercentage / $totalCourses)
            : 0;

        if ($result['overall']['totalQuestions'] > 0) {
            $result['overall']['correctPercentage'] = round(
                ($result['overall']['correctAnswers'] / $result['overall']['totalQuestions']) * 100,
                1
            );
        }

        if ($result['overall']['completed'] > 0) {
            $result['overall']['averagePercentage'] = round(
                $result['overall']['correctAnswers'] / $result['overall']['completed'] * 100,
                1
            );
        }

        return $result;
    }
}

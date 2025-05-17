<?php

namespace App\Controller\Api\Progress;

use App\Entity\User;
use Exception;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Bundle\SecurityBundle\Security;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

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

        /** @var User $user */
        $user = $this->security->getUser();

        try {
            // Прогресс по урокам с проверкой
            $lessonProgress = $user->getProgress() ?? ['byCourse' => [], 'overall' => []];
            $completedLessons = $user->getLessonProgresses()
                ? $user->getLessonProgresses()
                    ->filter(fn($p) => $p->isCompleted())
                    ->map(fn($p) => [
                        'lessonId' => $p->getLesson()->getId(),
                        'title' => $p->getLesson()->getTitle(),
                        'courseId' => $p->getLesson()->getCourse()->getId(),
                        'completedAt' => $p->getCompletedAt()->format('Y-m-d H:i:s')
                    ])->toArray()
                : [];

            // Прогресс по тестам с проверкой
            $quizProgress = $user->getQuizProgresses()
                ? $user->getQuizProgressStats()
                : ['byCourse' => [], 'overall' => [], 'completed' => []];

            $completedQuizzes = $user->getQuizProgresses()
                ? $user->getQuizProgresses()
                    ->filter(fn($p) => $p->isCompleted())
                    ->map(fn($p) => [
                        'quizId' => $p->getQuiz()->getId(),
                        'question' => $p->getQuiz()->getQuestion(),
                        'courseId' => $p->getQuiz()->getCourse()->getId(),
                        'score' => $p->getScore(),
                        'percentage' => $p->getScore(),
                        'correctAnswers' => $p->getCorrectAnswers(),
                        'totalQuestions' => $p->getTotalQuestions(),
                        'completedAt' => $p->getCompletedAt()->format('Y-m-d H:i:s')
                    ])->toArray()
                : [];

            $quizProgress['completed'] = $completedQuizzes;
            $quizProgress = $this->formatQuizResponse($quizProgress);

            $combined = $this->calculateCombinedProgress(
                $lessonProgress['byCourse'] ?? [],
                $quizProgress['progress']['byCourse'] ?? []
            );

            return $this->json([
                'lessons' => [
                    'progress' => $lessonProgress,
                    'completed' => $completedLessons
                ],
                'quizzes' => $quizProgress,
                'combinedProgress' => $combined
            ]);

        } catch (Exception $e) {
            return $this->json([
                'error' => 'Failed to get progress data',
                'details' => $e->getMessage()
            ], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }

    private function calculateCombinedProgress(array $lessons, array $quizzes): array
    {
        $courses = [];

        // Защита от null в уроках
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

        // Защита от null в тестах
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
            $completed = $course['lessonsCompleted'] + $course['quizzesCompleted'];
            $total = $course['lessonsTotal'] + $course['quizzesTotal'];
            $percentage = $total > 0 ? round(($completed / $total) * 100) : 0;
            $quizPercentage = $course['totalQuestions'] > 0
                ? round(($course['correctAnswers'] / $course['totalQuestions']) * 100, 1)
                : 0;

            $result['byCourse'][] = [
                'courseId' => $course['courseId'],
                'courseTitle' => $course['courseTitle'],
                'completed' => $completed,
                'total' => $total,
                'percentage' => $percentage,
                'details' => [
                    'lessons' => [
                        'completed' => $course['lessonsCompleted'],
                        'total' => $course['lessonsTotal'],
                        'percentage' => $course['lessonsTotal'] > 0
                            ? round(($course['lessonsCompleted'] / $course['lessonsTotal']) * 100)
                            : 0
                    ],
                    'quizzes' => [
                        'completed' => $course['quizzesCompleted'],
                        'total' => $course['quizzesTotal'],
                        'correctAnswers' => $course['correctAnswers'],
                        'totalQuestions' => $course['totalQuestions'],
                        'correctPercentage' => $quizPercentage,
                        'averagePercentage' => $course['quizzesCompleted'] > 0
                            ? round($course['correctAnswers'] / $course['quizzesCompleted'] * 100, 1)
                            : 0
                    ]
                ]
            ];

            $result['overall']['completed'] += $completed;
            $result['overall']['total'] += $total;
            $result['overall']['correctAnswers'] += $course['correctAnswers'];
            $result['overall']['totalQuestions'] += $course['totalQuestions'];
        }

        if ($result['overall']['total'] > 0) {
            $result['overall']['percentage'] = round(
                ($result['overall']['completed'] / $result['overall']['total']) * 100
            );
        }

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

    private function formatQuizResponse(array $quizProgress): array
    {
        // Добавляем проценты в completed quizzes
        foreach ($quizProgress['completed'] as &$quiz) {
            $quiz['percentage'] = $quiz['score'];
        }

        // Добавляем проценты в byCourse
        foreach ($quizProgress['progress']['byCourse'] as &$course) {
            $course['averagePercentage'] = $course['averageScore'];
            $course['details']['correctPercentage'] = $course['details']['totalQuestions'] > 0
                ? round(($course['details']['correctAnswers'] / $course['details']['totalQuestions']) * 100, 1)
                : 0;
        }

        // Добавляем проценты в overall
        $quizProgress['progress']['overall']['averagePercentage'] =
            $quizProgress['progress']['overall']['averageScore'];
        $quizProgress['progress']['overall']['correctPercentage'] =
            $quizProgress['progress']['overall']['totalQuestions'] > 0
                ? round(($quizProgress['progress']['overall']['totalCorrect'] /
                    $quizProgress['progress']['overall']['totalQuestions']) * 100, 1)
                : 0;

        return $quizProgress;
    }
}

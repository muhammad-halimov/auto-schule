<?php

namespace App\Controller\Api\Progress;

use App\Entity\User;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Bundle\SecurityBundle\Security;
use Symfony\Component\HttpFoundation\JsonResponse;
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

        // Прогресс по урокам
        $lessonProgress = $user->getProgress();
        $completedLessons = $user->getLessonProgresses()
            ->filter(fn($p) => $p->isCompleted())
            ->map(fn($p) => [
                'lessonId' => $p->getLesson()->getId(),
                'title' => $p->getLesson()->getTitle(),
                'courseId' => $p->getLesson()->getCourse()->getId(),
                'completedAt' => $p->getCompletedAt()->format('Y-m-d H:i:s')
            ])->toArray();

        // Прогресс по тестам
        $quizProgress = $user->getQuizProgressStats();
        $completedQuizzes = $user->getQuizProgresses()
            ->filter(fn($p) => $p->isCompleted())
            ->map(fn($p) => [
                'quizId' => $p->getQuiz()->getId(),
                'question' => $p->getQuiz()->getQuestion(),
                'courseId' => $p->getQuiz()->getCourse()->getId(),
                'score' => $p->getScore(),
                'correctAnswers' => $p->getCorrectAnswers(),
                'totalQuestions' => $p->getTotalQuestions(),
                'completedAt' => $p->getCompletedAt()->format('Y-m-d H:i:s')
            ])->toArray();

        // Комбинированный прогресс
        $combined = $this->calculateCombinedProgress(
            $lessonProgress['byCourse'],
            $quizProgress['byCourse']
        );

        return $this->json([
            'lessons' => [
                'progress' => $lessonProgress,
                'completed' => $completedLessons
            ],
            'quizzes' => [
                'progress' => $quizProgress,
                'completed' => $completedQuizzes
            ],
            'combinedProgress' => $combined
        ]);
    }

    private function calculateCombinedProgress(array $lessons, array $quizzes): array
    {
        $courses = [];

        // Обработка уроков
        foreach ($lessons as $lesson) {
            $courseId = $lesson['courseId'];
            $courses[$courseId] = [
                'courseId' => $courseId,
                'courseTitle' => $lesson['courseTitle'],
                'lessonsCompleted' => $lesson['completed'],
                'lessonsTotal' => $lesson['total'],
                'quizzesCompleted' => 0,
                'quizzesTotal' => 0,
                'correctAnswers' => 0,
                'totalQuestions' => 0
            ];
        }

        // Обработка тестов
        foreach ($quizzes as $quiz) {
            $courseId = $quiz['courseId'];
            if (!isset($courses[$courseId])) {
                $courses[$courseId] = [
                    'courseId' => $courseId,
                    'courseTitle' => $quiz['courseTitle'],
                    'lessonsCompleted' => 0,
                    'lessonsTotal' => 0,
                    'quizzesCompleted' => $quiz['completed'],
                    'quizzesTotal' => $quiz['total'],
                    'correctAnswers' => $quiz['details']['correctAnswers'],
                    'totalQuestions' => $quiz['details']['totalQuestions']
                ];
            } else {
                $courses[$courseId]['quizzesCompleted'] = $quiz['completed'];
                $courses[$courseId]['quizzesTotal'] = $quiz['total'];
                $courses[$courseId]['correctAnswers'] = $quiz['details']['correctAnswers'];
                $courses[$courseId]['totalQuestions'] = $quiz['details']['totalQuestions'];
            }
        }

        // Расчет итогов
        $result = ['byCourse' => [], 'overall' => [
            'completed' => 0,
            'total' => 0,
            'percentage' => 0,
            'correctAnswers' => 0,
            'totalQuestions' => 0
        ]];

        foreach ($courses as $course) {
            $completed = $course['lessonsCompleted'] + $course['quizzesCompleted'];
            $total = $course['lessonsTotal'] + $course['quizzesTotal'];
            $percentage = $total > 0 ? round(($completed / $total) * 100) : 0;

            $result['byCourse'][] = [
                'courseId' => $course['courseId'],
                'courseTitle' => $course['courseTitle'],
                'completed' => $completed,
                'total' => $total,
                'percentage' => $percentage,
                'details' => [
                    'lessons' => [
                        'completed' => $course['lessonsCompleted'],
                        'total' => $course['lessonsTotal']
                    ],
                    'quizzes' => [
                        'completed' => $course['quizzesCompleted'],
                        'total' => $course['quizzesTotal'],
                        'correctAnswers' => $course['correctAnswers'],
                        'totalQuestions' => $course['totalQuestions']
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

        return $result;
    }
}

<?php

namespace App\Controller\Api\Progress;

use App\Entity\CourseQuiz;
use App\Entity\StudentQuizProgress;
use App\Entity\User;
use Doctrine\ORM\EntityManagerInterface;
use Exception;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Bundle\SecurityBundle\Security;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/api/progress/quiz')]
class QuizProgressController extends AbstractController
{
    public function __construct(
        private readonly EntityManagerInterface $em,
        private readonly Security               $security
    ) {}

    #[Route('/update', name: 'api_progress_quiz_update', methods: ['POST'])]
    public function updateQuizProgress(Request $request): JsonResponse
    {
        $this->denyAccessUnlessGranted('IS_AUTHENTICATED_FULLY');

        /** @var User $user */
        $user = $this->security->getUser();
        $data = json_decode($request->getContent(), true);

        if (!isset($data['quizId'], $data['answers']))
            return $this->json(
                ['error' => 'quizId and answers are required'],
                Response::HTTP_BAD_REQUEST
            );

        $quiz = $this->em->getRepository(CourseQuiz::class)->find($data['quizId']);

        if (!$quiz)
            return $this->json(
                ['error' => 'Quiz not found'],
                Response::HTTP_NOT_FOUND
            );

        try {
            $user->markQuizCompleted($quiz, $data['answers']);
            $this->em->flush();

            return $this->json([
                'success' => true,
                'quizProgress' => $user->getQuizProgressStats()
            ]);
        } catch (Exception $e) {
            return $this->json(
                ['error' => $e->getMessage()],
                Response::HTTP_INTERNAL_SERVER_ERROR
            );
        }
    }

    #[Route('/batch-update', name: 'api_progress_quiz_batch_update', methods: ['POST'])]
    public function batchUpdateQuizProgress(Request $request): JsonResponse
    {
        $this->denyAccessUnlessGranted('IS_AUTHENTICATED_FULLY');

        /** @var User $user */
        $user = $this->security->getUser();
        $data = json_decode($request->getContent(), true);

        if (!is_array($data)) {
            return $this->json(
                ['error' => 'Expected array of quiz updates'],
                Response::HTTP_BAD_REQUEST
            );
        }

        $results = [];
        $hasErrors = false;

        foreach ($data as $item) {
            if (!isset($item['quizId'], $item['answers'])) {
                $hasErrors = true;
                $results[] = [
                    'quizId' => $item['quizId'] ?? null,
                    'success' => false,
                    'error' => 'Missing quizId or answers'
                ];
                continue;
            }

            $quiz = $this->em->getRepository(CourseQuiz::class)->find($item['quizId']);
            if (!$quiz) {
                $hasErrors = true;
                $results[] = [
                    'quizId' => $item['quizId'],
                    'success' => false,
                    'error' => 'Quiz not found'
                ];
                continue;
            }

            try {
                $user->markQuizCompleted($quiz, $item['answers']);
                $results[] = [
                    'quizId' => $item['quizId'],
                    'success' => true,
                    'score' => $user->getQuizProgress($quiz)->getScore()
                ];
            } catch (Exception $e) {
                $hasErrors = true;
                $results[] = [
                    'quizId' => $item['quizId'],
                    'success' => false,
                    'error' => $e->getMessage()
                ];
            }
        }

        $this->em->flush();

        return $this->json([
            'overallSuccess' => !$hasErrors,
            'results' => $results,
            'updatedProgress' => $user->getQuizProgressStats()
        ]);
    }

    #[Route('/delete', name: 'api_progress_quiz_delete', methods: ['DELETE'])]
    public function deleteQuizProgress(Request $request): JsonResponse
    {
        $this->denyAccessUnlessGranted('IS_AUTHENTICATED_FULLY');

        /** @var User $user */
        $user = $this->security->getUser();
        $data = json_decode($request->getContent(), true);

        if (!isset($data['quizId']))
            return $this->json(
                ['error' => 'quizId is required'],
                Response::HTTP_BAD_REQUEST
            );

        $progress = $this->em->getRepository(StudentQuizProgress::class)->findOneBy([
            'quiz' => $data['quizId'],
            'student' => $user->getId()
        ]);

        if (!$progress)
            return $this->json(
                ['error' => 'Progress not found'],
                Response::HTTP_NOT_FOUND
            );

        try {
            $this->em->remove($progress);
            $this->em->flush();

            return $this->json([
                'success' => true,
                'quizProgress' => $user->getQuizProgressStats()
            ]);
        } catch (Exception $e) {
            return $this->json(
                ['error' => $e->getMessage()],
                Response::HTTP_INTERNAL_SERVER_ERROR
            );
        }
    }
}
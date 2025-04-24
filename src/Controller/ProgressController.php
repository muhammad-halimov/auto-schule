<?php

namespace App\Controller;

use App\Entity\StudentLessonProgress;
use App\Entity\TeacherLesson;
use App\Entity\User;
use Doctrine\ORM\EntityManagerInterface;
use Exception;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Bundle\SecurityBundle\Security;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/api/progress', name: 'api_progress', methods: ['GET'])]
class ProgressController extends AbstractController
{
    public function __construct(
        private readonly EntityManagerInterface $em,
        private readonly Security $security
    ) {}

    #[Route('/', name: 'api_progress_get', methods: ['GET'])]
    public function getProgress(): JsonResponse
    {
        $this->denyAccessUnlessGranted('IS_AUTHENTICATED_FULLY');

        /** @var User $user */
        $user = $this->security->getUser();

        $completedLessons = array_map(
            fn($p) => [
                'lessonId' => $p->getLesson()->getId(),
                'lessonTitle' => $p->getLesson()->getTitle(),
                'courseId' => $p->getLesson()->getCourse()->getId(),
                'completedAt' => $p->getCompletedAt()->format('Y-m-d H:i:s')
            ],
            $user->getLessonProgresses()->filter(
                fn($p) => $p->isCompleted()
            )->toArray()
        );

        $progressData = $user->getProgress();

        return $this->json([
            'progress' => $progressData,
            'completedLessons' => $completedLessons
        ]);
    }

    #[Route('/update', name: 'api_progress_update', methods: ['POST'])]
    public function updateProgress(Request $request): JsonResponse
    {
        $this->denyAccessUnlessGranted('IS_AUTHENTICATED_FULLY');

        /** @var User $user */
        $user = $this->security->getUser();
        $data = json_decode($request->getContent(), true);
        if (!isset($data['lessonId'])) {
            return $this->json(['message' => 'Lesson ID is required'], Response::HTTP_BAD_REQUEST);
        }

        // 3. Find the lesson
        $lesson = $this->em->getRepository(TeacherLesson::class)->find($data['lessonId']);
        if (!$lesson) {
            return $this->json(['message' => 'Lesson not found'], Response::HTTP_NOT_FOUND);
        }

        try {
            // 4. Update progress
            $user->markLessonCompleted($lesson);
            $this->em->flush();

            return $this->json([
                'progress' => $user->getProgress(),
                'message' => 'Progress updated successfully'
            ]);

        } catch (Exception $e) {
            return $this->json([
                'message' => 'Error updating progress',
                'error' => $e->getMessage()
            ], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }

    #[Route('/delete', name: 'api_progress_delete', methods: ['DELETE'])]
    public function deleteLessonProgress(Request $request): JsonResponse
    {
        $this->denyAccessUnlessGranted('IS_AUTHENTICATED_FULLY');

        /** @var User $user */
        $user = $this->security->getUser();
        $data = json_decode($request->getContent(), true);

        if (!isset($data['lessonId']))
            return $this->json(['message' => 'Lesson ID is required'], Response::HTTP_BAD_REQUEST);

        // 3. Find the lesson
        $lesson = $this->em->getRepository(TeacherLesson::class)->find($data['lessonId']);
        if (!$lesson)
            return $this->json(['message' => 'Lesson not found'], Response::HTTP_NOT_FOUND);

        $progress = $this->em->getRepository(StudentLessonProgress::class)->findOneBy([
            'lesson' => $data['lessonId'],
            'student' => $user->getId()
        ]);

        if (!$progress)
            return $this->json(['message' => 'Progress record not found'], Response::HTTP_NOT_FOUND);

        try {
            $this->em->remove($progress);
            $this->em->flush();

            return $this->json([
                'progress' => $user->getProgress(),
                'message' => 'Progress deleted successfully',
            ]);
        } catch (Exception $e) {
            return $this->json([
                'message' => 'Error deleting progress',
                'error' => $e->getMessage()
            ], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }
}

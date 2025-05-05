<?php

namespace App\Controller\Api\Filter;

use App\Repository\InstructorLessonRepository;
use Exception;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;

class InstructorLessonStudentFilterController extends AbstractController
{
    private readonly InstructorLessonRepository $instructorLessonRepository;

    public function __construct(InstructorLessonRepository $instructorLessonRepository)
    {
        $this->instructorLessonRepository = $instructorLessonRepository;
    }

    public function __invoke(int $id): JsonResponse
    {
        try {
            $filteredLessons = $this->instructorLessonRepository->findStudentById($id);

            return empty($filteredLessons)
                ? $this->json([])
                : $this->json($filteredLessons, 200, [], ['groups' => ['instructorLessons:read']]);
        } catch (Exception $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'trace' => $e->getTrace()
            ], 500);
        }
    }
}

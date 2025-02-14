<?php

namespace App\Controller\Api\Filters;

use App\Repository\UserRepository;
use Exception;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;

class StudentFilterController extends AbstractController
{
    public function __construct(
        private readonly UserRepository $userRepository,
    )
    {
    }

    public function __invoke(): JsonResponse
    {
        try {
            $students = $this->userRepository->findByRole("ROLE_STUDENT");

            // Если нет студентов, возвращаем пустой массив
            if (empty($students))
                return $this->json([]);

            return $this->json($students, 200, [], ['groups' => ['students:read']]);
        } catch (Exception $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'trace' => $e->getTrace()
            ], 500);
        }
    }
}
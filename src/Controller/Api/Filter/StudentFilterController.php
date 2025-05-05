<?php

namespace App\Controller\Api\Filter;

use App\Repository\UserRepository;
use Exception;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;

class StudentFilterController extends AbstractController
{
    private readonly UserRepository $userRepository;

    public function __construct(UserRepository $userRepository)
    {
        $this->userRepository = $userRepository;
    }

    public function __invoke(): JsonResponse
    {
        try {
            $students = $this->userRepository->findByRole("ROLE_STUDENT");

            // Если нет студентов, возвращаем пустой массив
            return empty($students)
                ? $this->json([])
                : $this->json($students, 200, [], ['groups' => ['students:read']]);
        } catch (Exception $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'trace' => $e->getTrace()
            ], 500);
        }
    }
}
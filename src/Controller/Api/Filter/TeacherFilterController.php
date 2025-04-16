<?php

namespace App\Controller\Api\Filter;

use App\Repository\UserRepository;
use Exception;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;

class TeacherFilterController extends AbstractController
{
    private readonly UserRepository $userRepository;

    public function __construct(UserRepository $userRepository)
    {
        $this->userRepository = $userRepository;
    }

    public function __invoke(): JsonResponse
    {
        try {
            $students = $this->userRepository->findByRole("ROLE_TEACHER");

            if (empty($students))
                return $this->json([]);

            return $this->json($students, 200, [], ['groups' => ['teachers:read']]);
        } catch (Exception $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'trace' => $e->getTrace()
            ], 500);
        }
    }
}
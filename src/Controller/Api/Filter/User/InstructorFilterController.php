<?php

namespace App\Controller\Api\Filter\User;

use App\Repository\UserRepository;
use Exception;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;

class InstructorFilterController extends AbstractController
{
    private readonly UserRepository $userRepository;

    public function __construct(UserRepository $userRepository)
    {
        $this->userRepository = $userRepository;
    }

    public function __invoke(): JsonResponse
    {
        try {
            $instructors = $this->userRepository->findByRole("ROLE_INSTRUCTOR");

            return empty($instructors)
                ? $this->json([])
                : $this->json($instructors, 200, [], ['groups' => ['instructors:read']]);
        } catch (Exception $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'trace' => $e->getTrace()
            ], 500);
        }
    }
}
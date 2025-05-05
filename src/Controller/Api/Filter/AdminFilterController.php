<?php

namespace App\Controller\Api\Filter;

use App\Repository\UserRepository;
use Exception;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;

class AdminFilterController extends AbstractController
{
    private readonly UserRepository $userRepository;

    public function __construct(UserRepository $userRepository)
    {
        $this->userRepository = $userRepository;
    }

    public function __invoke(): JsonResponse
    {
        try {
            $admins = $this->userRepository->findByRole("ROLE_ADMIN");

            return empty($admins)
                ? $this->json([])
                : $this->json($admins, 200, [], ['groups' => ['admins:read']]);
        } catch (Exception $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'trace' => $e->getTrace()
            ], 500);
        }
    }
}
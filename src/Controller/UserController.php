<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\Security\Http\Attribute\CurrentUser;
use Symfony\Component\Security\Core\User\UserInterface;

class UserController extends AbstractController
{
    #[Route('/api/me', name: 'api_me', methods: ['GET'])]
    public function index(#[CurrentUser] ?UserInterface $user): JsonResponse
    {
        if (!$user) {
            return $this->json(['message' => 'Unauthorized'], Response::HTTP_UNAUTHORIZED);
        }

        if (!$user->getIsActive() || !$user->getIsApproved()) {
            return $this->json(['message' => 'Unauthorized'], Response::HTTP_UNAUTHORIZED);
        }

        return $this->json(data: [
            'id' => $user->getId(),
            'username' => $user->getUsername(),
            'name' => $user->getName(),
            'surname' => $user->getSurname(),
            'patronym' => $user->getPatronym(),
            'email' => $user->getEmail(),
            'phone' => $user->getPhone(),
            'dateOfBirth' => $user->getDateOfBirth(),
            'message' => $user->getMessage(),
            'image' => $user->getImage(),
        ]);
    }
}

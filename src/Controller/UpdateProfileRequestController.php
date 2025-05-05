<?php

namespace App\Controller;

use App\Entity\User;
use App\Service\UserProfileService;
use InvalidArgumentException;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/api/update-profile')]
class UpdateProfileRequestController extends AbstractController
{
    #[Route('', name: 'update_profile', methods: ['POST'])]
    public function __invoke(Request $request, UserProfileService $profileUpdater): JsonResponse
    {
        $this->denyAccessUnlessGranted('IS_AUTHENTICATED_FULLY');

        /** @var User $user */
        $user = $this->getUser();

        try {
            $profileUpdater->update($user, $request);
        } catch (InvalidArgumentException $e) {
            return $this->json(['Ошибка' => $e->getMessage()], 400);
        }

        return $this->json(['message' => 'Профиль успешно обновлён.']);
    }
}
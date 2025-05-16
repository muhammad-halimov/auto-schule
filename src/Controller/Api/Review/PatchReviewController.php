<?php

namespace App\Controller\Api\Review;

use App\Entity\User;
use App\Service\ReviewService;
use InvalidArgumentException;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/api/reviews')]
class PatchReviewController extends AbstractController
{
    private readonly ReviewService $reviewService;

    public function __construct(ReviewService $reviewService)
    {
        $this->reviewService = $reviewService;
    }

    #[Route('', name: 'patch_review', methods: ['PATCH'])]
    public function patchReview(Request $request): JsonResponse
    {
        $this->denyAccessUnlessGranted('IS_AUTHENTICATED_FULLY');

        $user = $this->getUser();
        $userRoles = $user?->getRoles() ?? [];
        $allowedRoles = array_values(User::ROLES);

        if (empty(array_intersect($allowedRoles, $userRoles))) {
            throw $this->createAccessDeniedException('Доступ запрещён.');
        }

        try {
            $this->reviewService->patchReview($request);
        } catch (InvalidArgumentException $e) {
            return $this->json(['Ошибка' => $e->getMessage()], 400);
        }

        return $this->json(['message' => 'Отзыв успешно обновлён.']);
    }
}

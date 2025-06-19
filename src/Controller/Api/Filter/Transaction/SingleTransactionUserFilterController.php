<?php

declare(strict_types=1);

namespace App\Controller\Api\Filter\Transaction;

use App\Entity\User;
use App\Repository\TransactionRepository;
use Exception;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Bundle\SecurityBundle\Security;
use Symfony\Component\HttpFoundation\JsonResponse;

class SingleTransactionUserFilterController extends AbstractController
{
    private readonly TransactionRepository $transactionRepository;
    private readonly Security $security;

    public function __construct(
        TransactionRepository $transactionRepository,
        Security              $security
    )
    {
        $this->transactionRepository = $transactionRepository;
        $this->security = $security;
    }

    public function __invoke(int $id): JsonResponse
    {
        try {
            $this->denyAccessUnlessGranted('IS_AUTHENTICATED_FULLY');

            /** @var User $user */
            $user = $this->security->getUser();
            $transaction = $this->transactionRepository->findUserTransactionById($id, $user->getId());

            if (!in_array('ROLE_STUDENT', $user->getRoles())) {
                throw $this->createAccessDeniedException('Доступ запрещён.');
            }

            return empty($transaction)
                ? $this->json([], 404)
                : $this->json($transaction, 200, [], ['groups' => ['transactions:read']]);
        } catch (Exception $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'trace' => $e->getTrace()
            ], 500);
        }
    }
}

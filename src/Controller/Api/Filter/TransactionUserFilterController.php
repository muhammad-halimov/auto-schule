<?php

declare(strict_types=1);

namespace App\Controller\Api\Filter;

use App\Repository\TransactionRepository;
use Exception;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;

class TransactionUserFilterController extends AbstractController
{
    private readonly TransactionRepository $transactionRepository;

    public function __construct(TransactionRepository $transactionRepository)
    {
        $this->transactionRepository = $transactionRepository;
    }

    public function __invoke(int $id): JsonResponse
    {
        try {
            $filteredTransactions = $this->transactionRepository->findUserById($id);

            return empty($filteredTransactions)
                ? $this->json([])
                : $this->json($filteredTransactions, 200, [], ['groups' => ['transactions:read']]);
        }
        catch (Exception $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'trace' => $e->getTrace()
            ], 500);
        }
    }
}

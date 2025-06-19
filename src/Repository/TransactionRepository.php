<?php

namespace App\Repository;

use App\Entity\Transaction;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\ORM\NonUniqueResultException;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @extends ServiceEntityRepository<Transaction>
 */
class TransactionRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Transaction::class);
    }

    public function findUserById(int $id): array
    {
        return $this
            ->createQueryBuilder('tr')
            ->join('tr.user', 'u')
            ->andWhere('u.id = :id')
            ->setParameter('id', $id)
            ->getQuery()
            ->getResult();
    }

    /**
     * @throws NonUniqueResultException
     */
    public function findUserTransactionById(int $transactionId, int $userId): ?Transaction
    {
        return $this
            ->createQueryBuilder('tr')
            ->join('tr.user', 'u')
            ->andWhere('u.id = :userId')
            ->andWhere('tr.id = :transactionsId')
            ->setParameter('userId', $userId)
            ->setParameter('transactionsId', $transactionId)
            ->getQuery()
            ->getOneOrNullResult();
    }
}

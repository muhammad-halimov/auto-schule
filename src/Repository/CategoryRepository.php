<?php

namespace App\Repository;

use App\Entity\Category;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @extends ServiceEntityRepository<Category>
 */
class CategoryRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Category::class);
    }

    public function findCategoryByStudentId(int $id): array
    {
        return $this
            ->createQueryBuilder('c')
            ->join('c.users', 's')
            ->andWhere('s.id = :id')
            ->setParameter('id', $id)
            ->getQuery()
            ->getResult();
    }

    public function findCategoryByDrivingType(): array
    {
        return $this
            ->createQueryBuilder('c')
            ->andWhere('c.type = :type')
            ->setParameter('type', 'driving')
            ->getQuery()
            ->getResult();
    }

    public function findCategoryByCourseType(): array
    {
        return $this
            ->createQueryBuilder('c')
            ->andWhere('c.type = :type')
            ->setParameter('type', 'course')
            ->getQuery()
            ->getResult();
    }
}

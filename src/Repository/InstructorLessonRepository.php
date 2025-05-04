<?php

namespace App\Repository;

use App\Entity\InstructorLesson;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @extends ServiceEntityRepository<InstructorLesson>
 */
class InstructorLessonRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, InstructorLesson::class);
    }

    public function findStudentById(int $id): array
    {
        return $this
            ->createQueryBuilder('il')
            ->join('il.student', 's')
            ->andWhere('s.id = :id')
            ->setParameter('id', $id)
            ->getQuery()
            ->getResult();
    }
}

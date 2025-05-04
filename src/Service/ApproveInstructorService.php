<?php /** @noinspection PhpPropertyOnlyWrittenInspection */

namespace App\Service;

use App\Entity\User;
use Doctrine\ORM\EntityManagerInterface;

readonly class ApproveInstructorService
{
    /**
     * @param EntityManagerInterface $entityManager
     * @param User $user
     */
    public function approveInstructor(EntityManagerInterface $entityManager, User $user): void
    {
        $user->setRoles(['ROLE_INSTRUCTOR']);
        $user->setIsApproved(true);
        $user->setIsActive(true);

        // Сохраняем изменения в базе данных
        $entityManager->flush();
    }
}
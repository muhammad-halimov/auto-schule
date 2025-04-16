<?php /** @noinspection PhpPropertyOnlyWrittenInspection */

namespace App\Service;

use App\Entity\User;
use Doctrine\ORM\EntityManagerInterface;

class ApproveStudentRequest
{
    /**
     * @param EntityManagerInterface $entityManager
     * @param User $user
     */
    public function approveStudent(EntityManagerInterface $entityManager, User $user): void
    {
        $user->setRoles(['ROLE_STUDENT']);
        $user->setIsApproved(true);
        $user->setIsActive(true);

        // Сохраняем изменения в базе данных
        $entityManager->flush();
    }
}
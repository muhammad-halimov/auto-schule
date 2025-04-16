<?php /** @noinspection PhpPropertyOnlyWrittenInspection */

namespace App\Service;

use App\Entity\User;
use Doctrine\ORM\EntityManagerInterface;

class ApproveAdminRequest
{
    /**
     * @param EntityManagerInterface $entityManager
     * @param User $user
     */
    public function approveAdmin(EntityManagerInterface $entityManager, User $user): void
    {
        $user->setRoles(['ROLE_ADMIN']);
        $user->setIsApproved(true);
        $user->setIsActive(true);

        // Сохраняем изменения в базе данных
        $entityManager->flush();
    }
}
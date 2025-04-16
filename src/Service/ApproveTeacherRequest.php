<?php /** @noinspection PhpPropertyOnlyWrittenInspection */

namespace App\Service;

use App\Entity\User;
use Doctrine\ORM\EntityManagerInterface;

class ApproveTeacherRequest
{
    /**
     * @param EntityManagerInterface $entityManager
     * @param User $user
     */
    public function approveTeacher(EntityManagerInterface $entityManager, User $user): void
    {
        $user->setRoles(['ROLE_TEACHER']);
        $user->setIsApproved(true);
        $user->setIsActive(true);

        // Сохраняем изменения в базе данных
        $entityManager->flush();
    }
}
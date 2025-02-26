<?php

namespace App\Service;

use App\Entity\User;
use Doctrine\ORM\EntityManagerInterface;
use Random\RandomException;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;

class ApproveUserRequest
{
    private UserPasswordHasherInterface $passwordHasher;

    public function __construct(UserPasswordHasherInterface $passwordHasher)
    {
        $this->passwordHasher = $passwordHasher;
    }

    /**
     * @throws RandomException
     */
    public function approveUser(EntityManagerInterface $entityManager, User $user): string
    {
        $user->setRoles(['ROLE_USER', 'ROLE_STUDENT']);
        $user->setIsApproved(true);
        $user->setIsActive(true);

        // Генерируем случайный пароль для пользователя
        $randomPassword = bin2hex(random_bytes(4)); // 8 символов
        $hashedPassword = $this->passwordHasher->hashPassword($user, $randomPassword);
        $user->setPassword($hashedPassword);

        // Сохраняем изменения в базе данных
        $entityManager->flush();

        return $randomPassword;  // Возвращаем сгенерированный пароль
    }
}
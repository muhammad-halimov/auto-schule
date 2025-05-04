<?php /** @noinspection PhpPropertyOnlyWrittenInspection */

namespace App\Service;

use App\Entity\User;
use Doctrine\ORM\EntityManagerInterface;
use Random\RandomException;
use Symfony\Component\Mailer\Mailer;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;

readonly class NewPasswordService
{
    private UserPasswordHasherInterface $passwordHasher;
    private Mailer $mailer;

    public function __construct(UserPasswordHasherInterface $passwordHasher)
    {
        $this->passwordHasher = $passwordHasher;
    }

    /**
     * @throws RandomException
     */
    public function newPasswordRequest(EntityManagerInterface $entityManager, User $user): string
    {
        // Генерируем случайный пароль для пользователя
        $randomPassword = bin2hex(random_bytes(4)); // 8 символов
        $hashedPassword = $this->passwordHasher->hashPassword($user, $randomPassword);
        $user->setPassword($hashedPassword);
        // TODO: отправить пароль пользователю по почте

        // Сохраняем изменения в базе данных
        $entityManager->flush();

        return $randomPassword;  // Возвращаем сгенерированный пароль
    }
}
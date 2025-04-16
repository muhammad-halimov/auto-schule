<?php

namespace App\Service;

use App\Entity\User;
use DateTime;
use Doctrine\ORM\EntityManagerInterface;
use Exception;
use InvalidArgumentException;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;

readonly class UserProfileUpdater
{
    public function __construct(
        private EntityManagerInterface      $em,
        private UserPasswordHasherInterface $passwordHasher
    ) {}

    public function update(User $user, Request $request): void
    {
        try {
            $data = json_decode($request->getContent(), true);

            $user->setUsername($data['username']);
            $user->setName($data['name']);
            $user->setSurname($data['surname']);
            $user->setPatronym($data['patronym'] ?? null);
            $user->setPhone($data['phone']);
            $user->setEmail($data['email']);
            $user->setMessage($data['message'] ?? null);
            $user->setDateOfBirth(new DateTime($data['dateOfBirth']));

            if (!empty($data['password'])) {
                $hashedPassword = $this->passwordHasher->hashPassword($user, $data['password']);
                $user->setPassword($hashedPassword);
            }

            $this->em->flush();
        } catch (Exception $exception) {
            throw new InvalidArgumentException("Произошла ошибка: {$exception->getMessage()}");
        }
    }
}
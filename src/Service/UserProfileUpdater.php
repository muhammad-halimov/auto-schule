<?php

namespace App\Service;

use App\Entity\User;
use DateTime;
use Doctrine\ORM\EntityManagerInterface;
use Exception;
use InvalidArgumentException;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;
use Vich\UploaderBundle\Handler\UploadHandler;

readonly class UserProfileUpdater
{
    public function __construct(
        private EntityManagerInterface $em,
        private UserPasswordHasherInterface $passwordHasher,
        private UploadHandler $uploadHandler
    ) {}

    public function update(User $user, Request $request): void
    {
        try {
            $data = $request->request->all();
            $files = $request->files->all();

            $user->setName($data['name']);
            $user->setSurname($data['surname']);
            $user->setPatronym($data['patronym'] ?? null);
            $user->setPhone($data['phone']);
            $user->setEmail($data['email']);
            $user->setMessage($data['message'] ?? null);
            $user->setDateOfBirth(new DateTime($data['dateOfBirth']));

            // Handle file upload with VichUploader
            if (isset($files['profile_photo'])) {
                $user->setImageFile($files['profile_photo']);
                $this->uploadHandler->upload($user, 'imageFile');
            }

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
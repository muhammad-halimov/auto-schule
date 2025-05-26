<?php

namespace App\Service;

use App\Entity\User;
use Doctrine\ORM\EntityManagerInterface;
use Exception;
use InvalidArgumentException;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;
use Vich\UploaderBundle\Handler\UploadHandler;

readonly class UserProfileService
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

            $user->setAboutMe($data['aboutMe'] ?? null);

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
            throw new InvalidArgumentException($exception->getMessage());
        }
    }
}
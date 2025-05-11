<?php

namespace App\Controller;

use App\Entity\AccountConfirmationToken;
use App\Form\CreatePasswordFormType;
use DateTime;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;
use Symfony\Component\Routing\Annotation\Route;

class AccountConfirmationController extends AbstractController
{
    #[Route(path: '/create-password/{token}', name: 'app_create_password')]
    public function createPassword(
        Request $request,
        string $token,
        EntityManagerInterface $entityManager,
        UserPasswordHasherInterface $passwordHasher
    ): Response
    {
        // Находим токен в базе
        $confirmationToken = $entityManager->getRepository(AccountConfirmationToken::class)
            ->findOneBy(criteria: ['token' => $token]);

        if (!$confirmationToken || $confirmationToken->getExpiresAt() < new DateTime()) {
            $this->addFlash(type: 'error', message: 'Ссылка для создания пароля недействительна или истек срок действия');
            return $this->redirect("{$_ENV["APP_URL"]}/auth.html");
        }

        $user = $confirmationToken->getUser();
        $form = $this->createForm(type: CreatePasswordFormType::class);
        $form->handleRequest(request: $request);

        if ($form->isSubmitted() && $form->isValid()) {
            // Устанавливаем пароль
            $user->setPassword(
                password: $passwordHasher->hashPassword(
                    user: $user,
                    plainPassword: $form->get(name: 'plainPassword')->getData()
                )
            );

            // Удаляем использованный токен
            $entityManager->remove($confirmationToken);
            $entityManager->flush();

            $this->addFlash(type: 'success', message: 'Пароль успешно создан! Теперь вы можете войти в систему.');
            return $this->redirect("{$_ENV["APP_URL"]}/auth.html");
        }

        return $this->render(view: 'account_confirmation/create_password.html.twig', parameters: [
            'form' => $form->createView()
        ]);
    }
}

<?php

namespace App\Controller;

use App\Entity\AccountConfirmationToken;
use App\Entity\User;
use App\Form\CreatePasswordFormType;
use App\Repository\UserRepository;
use App\Service\AccountConfirmationService;
use DateTime;
use Doctrine\ORM\EntityManagerInterface;
use Random\RandomException;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Bundle\SecurityBundle\Security;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Mailer\Exception\TransportExceptionInterface;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;
use Symfony\Component\Routing\Attribute\Route;

class AccountConfirmationController extends AbstractController
{
    private readonly AccountConfirmationService $accountConfirmationService;
    private readonly UserRepository             $userRepository;
    private readonly Security                   $security;

    public function __construct(
        AccountConfirmationService $accountConfirmationService,
        UserRepository             $userRepository,
        Security                   $security
    )
    {
        $this->accountConfirmationService = $accountConfirmationService;
        $this->userRepository = $userRepository;
        $this->security = $security;
    }

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

            return $this->redirect("{$_ENV["APP_URL"]}/auth.html");
        }

        return $this->render(view: 'account_confirmation/create_password.html.twig', parameters: [
            'form' => $form->createView()
        ]);
    }

    #[Route(path: '/api/create-password/{user_id}', name: 'app_create_password_by_user_id')]
    public function createPasswordByUserId(int $user_id): JsonResponse
    {
        $this->denyAccessUnlessGranted('IS_AUTHENTICATED_FULLY');

        /** @var User $user */
        $user = $this->userRepository->find($user_id);
        $admin = $this->security->getUser();

        if (!$user) {
            throw $this->createNotFoundException('Пользователь не найден.');
        } elseif (!$admin) {
            return new JsonResponse(['error' => 'Пользователь не аутентифицирован или токен истек.'], 401);
        }

        if (!in_array('ROLE_ADMIN', $admin->getRoles())) {
            throw $this->createAccessDeniedException('Доступ запрещён.');
        }

        try {
            return new JsonResponse($this->accountConfirmationService->sendConfirmationEmail($user));
        } catch (RandomException $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'trace' => $e->getTrace()
            ], 500);
        } catch (TransportExceptionInterface $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'trace' => $e->getTrace()
            ], 500);
        }
    }
}

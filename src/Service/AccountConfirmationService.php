<?php

namespace App\Service;

use App\Entity\User;
use App\Entity\AccountConfirmationToken;
use DateTime;
use Doctrine\ORM\EntityManagerInterface;
use Random\RandomException;
use Symfony\Component\Mailer\Exception\TransportExceptionInterface;
use Symfony\Component\Mailer\Mailer;
use Symfony\Component\Mailer\Transport;
use Symfony\Component\Mime\Email;
use Symfony\Component\Routing\Generator\UrlGeneratorInterface;

readonly class AccountConfirmationService
{
    public function __construct(
        private EntityManagerInterface $entityManager,
        private UrlGeneratorInterface  $urlGenerator
    ) {
    }

    /**
     * @throws RandomException
     * @throws TransportExceptionInterface
     */
    public function sendConfirmationEmail(User $user): string
    {
        $transport = Transport::fromDsn($_ENV['MAILER_DSN']);
        $transport->getStream()->setTimeout(2000);
        $mailer = new Mailer($transport);

        // Удаляем старые токены для этого пользователя
        $oldTokens = $this->entityManager->getRepository(AccountConfirmationToken::class)
            ->findBy(['user' => $user]);

        foreach ($oldTokens as $token) {
            $this->entityManager->remove($token);
        }

        // Создаем новый токен
        $token = new AccountConfirmationToken();
        $token->setUser($user);
        $token->setToken(bin2hex(random_bytes(32)));
        $token->setExpiresAt(new DateTime('+24 hours'));

        $this->entityManager->persist($token);
        $this->entityManager->flush();

        // Генерируем ссылку для подтверждения
        $confirmationUrl = $_ENV["ADMIN_URL"] . $this->urlGenerator->generate(
            'app_create_password',
            ['token' => $token->getToken()]
        );

        // Отправляем письмо
        $email = (new Email())
            ->from($_ENV['MAILER_SENDER'])
            ->to($user->getEmail())
            ->subject('Завершение регистрации')
            ->html("
                <h1>Завершение регистрации</h1>
                <p>Для завершения регистрации и создания пароля перейдите по ссылке:</p>
                <a href=\"$confirmationUrl\">$confirmationUrl</a>
                <p>Ссылка действительна 24 часа.</p>
            ");

        $mailer->send($email);

        return "Почта отправлено пользователю {$user->getEmail()}";
    }
}
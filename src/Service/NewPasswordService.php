<?php

namespace App\Service;

use App\Entity\User;
use Symfony\Component\Mailer\Exception\TransportExceptionInterface;
use Symfony\Component\Mailer\MailerInterface;
use Symfony\Component\Mime\Email;

readonly class NewPasswordService
{
    public function __construct(private MailerInterface $mailer){}

    /**
     * @throws TransportExceptionInterface
     */
    public function newPasswordRequest(User $user): void
    {
        $message = new Email();
        $message->from("muhammadi.halimov@icloud.com");
        $message->to("bobojonhalimzoda05@gmail.com");
        // $message->to($user->getEmail());
        $message->html("<h1>Hello from icloud</h1>");
        $message->subject("New Password");

        $this->mailer->send($message);
    }
}
<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\Mailer\Exception\TransportExceptionInterface;
use Symfony\Component\Mailer\MailerInterface;
use Symfony\Component\Mime\Email;
use Symfony\Component\Routing\Attribute\Route;

class MailerController extends AbstractController
{
    /**
     * @throws TransportExceptionInterface
     */
    #[Route('/verify-password')]
    public function sendEmail(MailerInterface $mailer): JsonResponse
    {
        $email = (new Email())
            ->from("muhammadi.halimov@icloud.com")
            ->to("bobojonhalimzoda05@gmail.com")
            ->subject('Hello from icloud!')
            ->text('Hello from icloud!')
            ->html("<h1>Hello from icloud!</h1>");

        $mailer->send($email);

        return $this->json("message has been sent");
    }
}

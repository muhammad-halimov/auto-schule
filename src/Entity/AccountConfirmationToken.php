<?php

namespace App\Entity;

use DateTimeInterface;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity]
class AccountConfirmationToken
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\ManyToOne(targetEntity: User::class)]
    #[ORM\JoinColumn(nullable: false)]
    private User $user;

    #[ORM\Column(type: 'string', length: 255, unique: true)]
    private string $token;

    #[ORM\Column(type: 'datetime')]
    private DateTimeInterface $expiresAt;

    public function getId(): ?int { return $this->id; }
    public function getUser(): User { return $this->user; }
    public function setUser(User $user): void { $this->user = $user; }
    public function getToken(): string { return $this->token; }
    public function setToken(string $token): void { $this->token = $token; }
    public function getExpiresAt(): DateTimeInterface { return $this->expiresAt; }
    public function setExpiresAt(DateTimeInterface $expiresAt): void { $this->expiresAt = $expiresAt; }
}
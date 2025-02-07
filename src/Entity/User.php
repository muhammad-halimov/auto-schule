<?php

namespace App\Entity;

use ApiPlatform\Metadata\ApiResource;
use ApiPlatform\Metadata\Get;
use ApiPlatform\Metadata\GetCollection;
use ApiPlatform\Metadata\Patch;
use ApiPlatform\Metadata\Post;
use App\Entity\Traits\CreatedAtTrait;
use App\Entity\Traits\UpdatedAtTrait;
use App\Repository\UserRepository;
use DateTime;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Security\Core\User\PasswordAuthenticatedUserInterface;
use Symfony\Component\Security\Core\User\UserInterface;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\Entity(repositoryClass: UserRepository::class)]
#[ORM\Table(name: 'user')]
#[ORM\HasLifecycleCallbacks]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Post(),
        new Patch(),
    ],
    normalizationContext: ['groups' => ['users:read']],
    paginationEnabled: false,
)]
class User implements UserInterface, PasswordAuthenticatedUserInterface
{
    public function __toString()
    {
        return $this->name.' '.$this->surname;
    }

    use UpdatedAtTrait;
    use CreatedAtTrait;

    public const ROLES = [
        'Администратор' => 'ROLE_ADMIN',
        'Студент' => 'ROLE_STUDENT',
        'Инструктор' => 'ROLE_INSTRUCTOR',
    ];

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer', nullable: false)]
    #[Groups(['users:read'])]
    private ?int $id = null;

    #[ORM\Column(type: 'string', length: 255, unique: true, nullable: true)]
    #[Groups(['users:read'])]
    private ?string $username = null;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['users:read'])]
    private ?string $name = null;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['users:read'])]
    private ?string $surname = null;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['users:read'])]
    private ?string $patronym = null;

    #[ORM\Column(type: 'string', length: 15, nullable: true)]
    #[Groups(['users:read'])]
    private ?string $phone = null;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['users:read'])]
    private ?string $email = null;

    #[ORM\Column(type: 'datetime', nullable: true)]
    #[Groups(['users:read'])]
    private ?DateTime $dateOfBirth = null;

    #[ORM\Column(type: 'json')]
    #[Groups(['users:read'])]
    private array $roles = [];

    #[ORM\Column(type: 'string')]
    private string $password;

    private ?string $plainPassword = null;

    /**
     * @return string|null
     */
    public function getPlainPassword(): ?string
    {
        return $this->plainPassword;
    }

    /**
     * @param string|null $plainPassword
     */
    public function setPlainPassword(?string $plainPassword): void
    {
        $this->plainPassword = $plainPassword;
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getUsername(): ?string
    {
        return $this->username;
    }

    public function setUsername(string $username): self
    {
        $this->username = $username;

        return $this;
    }

    public function getName(): ?string
    {
        return $this->name;
    }

    public function setName(?string $name): User
    {
        $this->name = $name;
        return $this;
    }

    public function getSurname(): ?string
    {
        return $this->surname;
    }

    public function setSurname(?string $surname): User
    {
        $this->surname = $surname;
        return $this;
    }

    public function getPatronym(): ?string
    {
        return $this->patronym;
    }

    public function setPatronym(?string $patronym): User
    {
        $this->patronym = $patronym;
        return $this;
    }

    public function getPhone(): ?string
    {
        return $this->phone;
    }

    public function setPhone(?string $phone): User
    {
        $this->phone = $phone;
        return $this;
    }

    public function getEmail(): ?string
    {
        return $this->email;
    }

    public function setEmail(?string $email): User
    {
        $this->email = $email;
        return $this;
    }

    public function getDateOfBirth(): ?DateTime
    {
        return $this->dateOfBirth;
    }

    public function setDateOfBirth(?DateTime $dateOfBirth): User
    {
        $this->dateOfBirth = $dateOfBirth;
        return $this;
    }

    /**
     * A visual identifier that represents this user.
     *
     * @see UserInterface
     */
    public function getUserIdentifier(): string
    {
        return (string) $this->username;
    }

    /**
     * @see UserInterface
     */
    public function getRoles(): array
    {
        $roles = $this->roles;
        // guarantee every user at least has ROLE_USER
        $roles[] = 'ROLE_USER';

        return array_unique($roles);
    }

    public function setRoles(array $roles): self
    {
        $this->roles = $roles;

        return $this;
    }

    /**
     * @see PasswordAuthenticatedUserInterface
     */
    public function getPassword(): string
    {
        return $this->password;
    }

    public function setPassword(string $password): self
    {
        $this->password = $password;

        return $this;
    }

    /**
     * @see UserInterface
     */
    public function eraseCredentials(): void
    {
        // If you store any temporary, sensitive data on the user, clear it here
        // $this->plainPassword = null;
    }
}

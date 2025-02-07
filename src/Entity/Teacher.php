<?php

namespace App\Entity;

use ApiPlatform\Metadata\ApiResource;
use ApiPlatform\Metadata\Get;
use ApiPlatform\Metadata\GetCollection;
use ApiPlatform\Metadata\Patch;
use ApiPlatform\Metadata\Post;
use App\Entity\Traits\CreatedAtTrait;
use App\Entity\Traits\UpdatedAtTrait;
use App\Repository\TeacherRepository;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Security\Core\User\PasswordAuthenticatedUserInterface;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\HasLifecycleCallbacks]
#[ORM\Table(name: 'teacher')]
#[ORM\Entity(repositoryClass: TeacherRepository::class)]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Post(),
        new Patch(),
    ],
    normalizationContext: ['groups' => ['teachers:read']],
    paginationEnabled: false,
)]
class Teacher implements PasswordAuthenticatedUserInterface
{
    public function __toString()
    {
        return $this->name.' '.$this->surname.' - '.$this->classTitle;
    }

    use UpdatedAtTrait;
    use CreatedAtTrait;

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups(['courses:read', 'students:read', 'teachers:read'])]
    private ?int $id = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['courses:read', 'students:read', 'teachers:read'])]
    private ?string $username = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['courses:read', 'students:read', 'teachers:read'])]
    private ?string $name = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['courses:read', 'students:read', 'teachers:read'])]
    private ?string $surname = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['courses:read', 'students:read', 'teachers:read'])]
    private ?string $patronym = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['courses:read', 'students:read', 'teachers:read'])]
    private ?string $classTitle = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['courses:read', 'students:read', 'teachers:read'])]
    private ?string $license = null;

    #[ORM\OneToOne(mappedBy: 'instructor', cascade: ['persist', 'remove'])]
    #[Groups(['teachers:read'])]
    private ?TeacherLesson $teacherLesson = null;

    #[ORM\Column(length: 255, nullable: true)]
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

    public function setUsername(?string $username): static
    {
        $this->username = $username;

        return $this;
    }

    public function getName(): ?string
    {
        return $this->name;
    }

    public function setName(?string $name): static
    {
        $this->name = $name;

        return $this;
    }

    public function getSurname(): ?string
    {
        return $this->surname;
    }

    public function setSurname(?string $surname): static
    {
        $this->surname = $surname;

        return $this;
    }

    public function getPatronym(): ?string
    {
        return $this->patronym;
    }

    public function setPatronym(?string $patronym): static
    {
        $this->patronym = $patronym;

        return $this;
    }

    public function getClassTitle(): ?string
    {
        return $this->classTitle;
    }

    public function setClassTitle(?string $classTitle): static
    {
        $this->classTitle = $classTitle;

        return $this;
    }

    public function getLicense(): ?string
    {
        return $this->license;
    }

    public function setLicense(?string $license): static
    {
        $this->license = $license;

        return $this;
    }

    public function getTeacherLesson(): ?TeacherLesson
    {
        return $this->teacherLesson;
    }

    public function setTeacherLesson(?TeacherLesson $teacherLesson): static
    {
        // unset the owning side of the relation if necessary
        if ($teacherLesson === null && $this->teacherLesson !== null) {
            $this->teacherLesson->setInstructor(null);
        }

        // set the owning side of the relation if necessary
        if ($teacherLesson !== null && $teacherLesson->getInstructor() !== $this) {
            $teacherLesson->setInstructor($this);
        }

        $this->teacherLesson = $teacherLesson;

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
}

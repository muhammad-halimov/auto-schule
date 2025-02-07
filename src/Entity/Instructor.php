<?php

namespace App\Entity;

use ApiPlatform\Metadata\ApiResource;
use ApiPlatform\Metadata\Get;
use ApiPlatform\Metadata\GetCollection;
use ApiPlatform\Metadata\Patch;
use ApiPlatform\Metadata\Post;
use App\Entity\Traits\CreatedAtTrait;
use App\Entity\Traits\UpdatedAtTrait;
use App\Repository\InstructorRepository;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Security\Core\User\PasswordAuthenticatedUserInterface;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\HasLifecycleCallbacks]
#[ORM\Table(name: 'instructor')]
#[ORM\Entity(repositoryClass: InstructorRepository::class)]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Post(),
        new Patch(),
    ],
    normalizationContext: ['groups' => ['instructors:read']],
    paginationEnabled: false,
)]
class Instructor implements PasswordAuthenticatedUserInterface
{
    public function __toString()
    {
        return $this->name.' '.$this->surname.' - '.$this->carMark.' '.$this->carModel;
    }

    use UpdatedAtTrait;
    use CreatedAtTrait;

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups(['instructors:read', 'instructorLessons:read', 'students:read'])]
    private ?int $id = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['instructors:read', 'instructorLessons:read', 'students:read'])]
    private ?string $username = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['instructors:read', 'instructorLessons:read', 'students:read'])]
    private ?string $name = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['instructors:read', 'instructorLessons:read', 'students:read'])]
    private ?string $surname = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['instructors:read', 'instructorLessons:read', 'students:read'])]
    private ?string $patronym = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['instructors:read', 'instructorLessons:read', 'students:read'])]
    private ?string $carMark = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['instructors:read', 'instructorLessons:read', 'students:read'])]
    private ?string $carModel = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['instructors:read', 'instructorLessons:read', 'students:read'])]
    private ?string $stateNumber = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['instructors:read', 'instructorLessons:read', 'students:read'])]
    private ?string $license = null;

    #[ORM\OneToOne(mappedBy: 'instructor', cascade: ['persist', 'remove'])]
    #[Groups(['instructors:read'])]
    private ?InstructorLesson $instructorLesson = null;

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

    public function getCarMark(): ?string
    {
        return $this->carMark;
    }

    public function setCarMark(?string $carMark): static
    {
        $this->carMark = $carMark;

        return $this;
    }

    public function getCarModel(): ?string
    {
        return $this->carModel;
    }

    public function setCarModel(?string $carModel): static
    {
        $this->carModel = $carModel;

        return $this;
    }

    public function getStateNumber(): ?string
    {
        return $this->stateNumber;
    }

    public function setStateNumber(?string $stateNumber): static
    {
        $this->stateNumber = $stateNumber;

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

    public function getInstructorLesson(): ?InstructorLesson
    {
        return $this->instructorLesson;
    }

    public function setInstructorLesson(?InstructorLesson $instructorLesson): static
    {
        // unset the owning side of the relation if necessary
        if ($instructorLesson === null && $this->instructorLesson !== null) {
            $this->instructorLesson->setInstructor(null);
        }

        // set the owning side of the relation if necessary
        if ($instructorLesson !== null && $instructorLesson->getInstructor() !== $this) {
            $instructorLesson->setInstructor($this);
        }

        $this->instructorLesson = $instructorLesson;

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

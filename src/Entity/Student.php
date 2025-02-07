<?php

namespace App\Entity;

use ApiPlatform\Metadata\ApiResource;
use ApiPlatform\Metadata\Get;
use ApiPlatform\Metadata\GetCollection;
use ApiPlatform\Metadata\Patch;
use ApiPlatform\Metadata\Post;
use App\Entity\Traits\CreatedAtTrait;
use App\Entity\Traits\UpdatedAtTrait;
use App\Repository\StudentRepository;
use DateTimeInterface;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Security\Core\User\PasswordAuthenticatedUserInterface;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\Table(name: 'student')]
#[ORM\HasLifecycleCallbacks]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Post(),
        new Patch(),
    ],
    normalizationContext: ['groups' => ['students:read']],
    paginationEnabled: false,
)]
#[ORM\Entity(repositoryClass: StudentRepository::class)]
class Student implements PasswordAuthenticatedUserInterface
{
    public function __toString()
    {
        return $this->name.' '.$this->surname;
    }

    use UpdatedAtTrait;
    use CreatedAtTrait;

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups(['courses:read', 'exams:read', 'students:read'])]
    private ?int $id = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['courses:read', 'exams:read', 'students:read'])]
    private ?string $username = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['courses:read', 'exams:read', 'students:read'])]
    private ?string $name = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['courses:read', 'exams:read', 'students:read'])]
    private ?string $surname = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['courses:read', 'exams:read', 'students:read'])]
    private ?string $patronym = null;

    #[ORM\Column(length: 15, nullable: true)]
    #[Groups(['students:read'])]
    private ?string $phone = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['students:read'])]
    private ?string $email = null;

    #[ORM\Column(type: Types::DATE_MUTABLE, nullable: true)]
    #[Groups(['students:read'])]
    private ?DateTimeInterface $dateOfBirth = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['courses:read', 'exams:read'])]
    private ?string $contract = null;

    #[ORM\Column(nullable: true)]
    #[Groups(['students:read'])]
    private ?bool $examStatus = null;

    #[ORM\OneToOne(inversedBy: 'student', cascade: ['persist', 'remove'])]
    #[Groups(['students:read'])]
    private ?Course $course = null;

    #[ORM\ManyToOne(inversedBy: 'students')]
    #[Groups(['students:read'])]
    private ?Exam $exam = null;

    #[ORM\OneToOne(mappedBy: 'student', cascade: ['persist', 'remove'])]
    #[Groups(['students:read'])]
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

    public function setPatronym(?string $patronym): Student
    {
        $this->patronym = $patronym;
        return $this;
    }

    public function getPhone(): ?string
    {
        return $this->phone;
    }

    public function setPhone(?string $phone): static
    {
        $this->phone = $phone;

        return $this;
    }

    public function getEmail(): ?string
    {
        return $this->email;
    }

    public function setEmail(?string $email): static
    {
        $this->email = $email;

        return $this;
    }

    public function getDateOfBirth(): ?DateTimeInterface
    {
        return $this->dateOfBirth;
    }

    public function setDateOfBirth(?DateTimeInterface $dateOfBirth): static
    {
        $this->dateOfBirth = $dateOfBirth;

        return $this;
    }

    public function getContract(): ?string
    {
        return $this->contract;
    }

    public function setContract(?string $contract): static
    {
        $this->contract = $contract;

        return $this;
    }

    public function isExamStatus(): ?bool
    {
        return $this->examStatus;
    }

    public function setExamStatus(?bool $examStatus): static
    {
        $this->examStatus = $examStatus;

        return $this;
    }

    public function getCourse(): ?Course
    {
        return $this->course;
    }

    public function setCourse(?Course $course): static
    {
        $this->course = $course;

        return $this;
    }

    public function getExam(): ?Exam
    {
        return $this->exam;
    }

    public function setExam(?Exam $exam): static
    {
        $this->exam = $exam;

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
            $this->instructorLesson->setStudent(null);
        }

        // set the owning side of the relation if necessary
        if ($instructorLesson !== null && $instructorLesson->getStudent() !== $this) {
            $instructorLesson->setStudent($this);
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

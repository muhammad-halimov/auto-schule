<?php

namespace App\Entity;

use ApiPlatform\Metadata\ApiResource;
use ApiPlatform\Metadata\Get;
use ApiPlatform\Metadata\GetCollection;
use ApiPlatform\Metadata\Patch;
use ApiPlatform\Metadata\Post;
use App\Entity\Traits\CreatedAtTrait;
use App\Entity\Traits\UpdatedAtTrait;
use App\Repository\InstructorLessonRepository;
use DateTimeInterface;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\Table(name: 'instructorLesson')]
#[ORM\HasLifecycleCallbacks]
#[ORM\Entity(repositoryClass: InstructorLessonRepository::class)]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Post(),
        new Patch(),
    ],
    normalizationContext: ['groups' => ['instructorLessons:read']],
    paginationEnabled: false,
)]
class InstructorLesson
{
    public function __toString(): string
    {
        return $this->title;
    }

    use UpdatedAtTrait;
    use CreatedAtTrait;

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups(['instructors:read', 'instructorLessons:read', 'students:read'])]
    private ?int $id = null;

    #[ORM\Column(type: Types::STRING, nullable: true)]
    #[Groups(['instructors:read', 'instructorLessons:read', 'students:read'])]
    private ?string $title = null;

    #[ORM\OneToOne(inversedBy: 'instructor', cascade: ['persist', 'remove'])]
    #[Groups(['instructorLessons:read', 'students:read'])]
    private ?User $instructor = null;

    #[ORM\Column(type: Types::DATETIME_MUTABLE, nullable: true)]
    #[Groups(['instructors:read', 'instructorLessons:read', 'students:read'])]
    private ?DateTimeInterface $date = null;

    #[ORM\Column(type: Types::DECIMAL, precision: 10, scale: 0, nullable: true)]
    #[Groups(['instructors:read', 'instructorLessons:read', 'students:read'])]
    private ?string $price = null;

    #[ORM\OneToOne(inversedBy: 'instructorLesson', cascade: ['persist', 'remove'])]
    private ?User $student = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getInstructor(): ?User
    {
        return $this->instructor;
    }

    public function setInstructor(?User $instructor): static
    {
        $this->instructor = $instructor;

        return $this;
    }

    public function getDate(): ?DateTimeInterface
    {
        return $this->date;
    }

    public function setDate(?DateTimeInterface $date): static
    {
        $this->date = $date;

        return $this;
    }

    public function getPrice(): ?string
    {
        return $this->price;
    }

    public function setPrice(string $price): static
    {
        $this->price = $price;

        return $this;
    }

    public function getTitle(): ?string
    {
        return $this->title;
    }

    public function setTitle(?string $title): InstructorLesson
    {
        $this->title = $title;
        return $this;
    }

    public function getStudent(): ?User
    {
        return $this->student;
    }

    public function setStudent(?User $student): static
    {
        $this->student = $student;

        return $this;
    }
}

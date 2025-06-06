<?php

namespace App\Entity;

use ApiPlatform\Metadata\ApiResource;
use ApiPlatform\Metadata\Delete;
use ApiPlatform\Metadata\Get;
use ApiPlatform\Metadata\GetCollection;
use ApiPlatform\Metadata\Patch;
use ApiPlatform\Metadata\Post;
use App\Controller\Api\Filter\InstructorLessonStudentFilterController;
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
        new Get(security: "
            is_granted('ROLE_ADMIN') or
            is_granted('ROLE_INSTRUCTOR') or
            is_granted('ROLE_STUDENT')
        "),
        new GetCollection(security: "
            is_granted('ROLE_ADMIN') or
            is_granted('ROLE_INSTRUCTOR') or
            is_granted('ROLE_STUDENT')
        "),
        new GetCollection(
            uriTemplate: '/instructor_lessons_filtered/{id}',
            controller: InstructorLessonStudentFilterController::class,
            security: "
                is_granted('ROLE_ADMIN') or
                is_granted('ROLE_INSTRUCTOR') or
                is_granted('ROLE_STUDENT')
        "),
        new Post(security: "
            is_granted('ROLE_ADMIN') or
            is_granted('ROLE_INSTRUCTOR') or
            is_granted('ROLE_STUDENT')
        "),
        new Patch(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_INSTRUCTOR')"),
        new Delete(security: "
            is_granted('ROLE_ADMIN') or 
            is_granted('ROLE_INSTRUCTOR') or 
            is_granted('ROLE_STUDENT')
        "),
    ],
    normalizationContext: ['groups' => ['instructorLessons:read']],
    paginationEnabled: false,
)]
class InstructorLesson
{
    use UpdatedAtTrait, CreatedAtTrait;

    public function __toString(): string
    {
        return $this->title ?? 'Без названия';
    }

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups(['instructors:read', 'instructorLessons:read', 'students:read'])]
    private ?int $id = null;

    #[ORM\ManyToOne(inversedBy: 'instructorLesson')]
    #[ORM\JoinColumn(name: "teacher_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups(['instructorLessons:read'])]
    private ?User $instructor = null;

    #[ORM\ManyToOne(inversedBy: 'instructorLessonStudent')]
    #[ORM\JoinColumn(name: "student_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups(['instructorLessons:read'])]
    private ?User $student = null;

    #[ORM\Column(type: Types::DATETIME_MUTABLE, nullable: true)]
    #[Groups(['instructors:read', 'instructorLessons:read', 'students:read'])]
    private ?DateTimeInterface $date = null;

    #[ORM\ManyToOne(inversedBy: 'instructorLessons')]
    #[ORM\JoinColumn(name: "autodrome_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups(['instructorLessons:read'])]
    private ?Autodrome $autodrome = null;

    #[ORM\ManyToOne(inversedBy: 'instructorLessons')]
    #[ORM\JoinColumn(name: "category_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups(['instructorLessons:read'])]
    private ?Category $category = null;

    public function getId(): ?int
    {
        return $this->id;
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

    public function getInstructor(): ?User
    {
        return $this->instructor;
    }

    public function setInstructor(?User $instructor): static
    {
        $this->instructor = $instructor;

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

    public function getAutodrome(): ?Autodrome
    {
        return $this->autodrome;
    }

    public function setAutodrome(?Autodrome $autodrome): static
    {
        $this->autodrome = $autodrome;

        return $this;
    }

    public function getCategory(): ?Category
    {
        return $this->category;
    }

    public function setCategory(?Category $category): static
    {
        $this->category = $category;

        return $this;
    }
}

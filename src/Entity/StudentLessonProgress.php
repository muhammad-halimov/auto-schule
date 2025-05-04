<?php

namespace App\Entity;

use ApiPlatform\Metadata\ApiResource;
use ApiPlatform\Metadata\Delete;
use ApiPlatform\Metadata\Get;
use ApiPlatform\Metadata\GetCollection;
use ApiPlatform\Metadata\Patch;
use ApiPlatform\Metadata\Post;
use App\Entity\Traits\CreatedAtTrait;
use App\Entity\Traits\UpdatedAtTrait;
use App\Repository\StudentLessonProgressRepository;
use DateTime;
use DateTimeInterface;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\Table(name: 'student_lesson_progress')]
#[ORM\HasLifecycleCallbacks]
#[ORM\Entity(repositoryClass: StudentLessonProgressRepository::class)]
#[ApiResource(
    operations: [
        new GetCollection(security: "is_granted('ROLE_ADMIN')"),
        new Get(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_STUDENT')"),
        new Patch(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_STUDENT')"),
        new Post(security: "is_granted('ROLE_ADMIN')"),
        new Delete(security: "is_granted('ROLE_ADMIN')")
    ],
    normalizationContext: ['groups' => ['progress:read']],
    denormalizationContext: ['groups' => ['progress:write']]
)]
class StudentLessonProgress
{
    use createdAtTrait, updatedAtTrait;

    #[ORM\Id]
    #[ORM\ManyToOne(targetEntity: User::class, inversedBy: 'lessonProgresses')]
    #[ORM\JoinColumn(nullable: false)]
    #[Groups(['progress:read'])]
    private User $student;

    #[ORM\Id]
    #[ORM\ManyToOne(targetEntity: TeacherLesson::class)]
    #[ORM\JoinColumn(nullable: false)]
    #[Groups(['progress:read', 'progress:write'])]
    private TeacherLesson $lesson;

    #[ORM\Column(type: 'boolean')]
    #[Groups(['progress:read', 'progress:write'])]
    private bool $isCompleted = false;

    #[ORM\Column(type: 'datetime', nullable: true)]
    #[Groups(['progress:read'])]
    private ?DateTimeInterface $completedAt = null;

    // Getters and setters
    public function getStudent(): User
    {
        return $this->student;
    }

    public function setStudent(User $student): self
    {
        $this->student = $student;
        return $this;
    }

    public function getLesson(): TeacherLesson
    {
        return $this->lesson;
    }

    public function setLesson(TeacherLesson $lesson): self
    {
        $this->lesson = $lesson;
        return $this;
    }

    public function isCompleted(): bool
    {
        return $this->isCompleted;
    }

    public function setIsCompleted(bool $isCompleted): self
    {
        $this->isCompleted = $isCompleted;
        $this->completedAt = $isCompleted ? new DateTime() : null;
        return $this;
    }

    public function getCompletedAt(): ?DateTimeInterface
    {
        return $this->completedAt;
    }
}
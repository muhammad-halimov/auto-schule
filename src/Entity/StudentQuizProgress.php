<?php

namespace App\Entity;

use ApiPlatform\Metadata\ApiResource;
use ApiPlatform\Metadata\Delete;
use ApiPlatform\Metadata\Get;
use ApiPlatform\Metadata\GetCollection;
use ApiPlatform\Metadata\Post;
use App\Entity\Traits\CreatedAtTrait;
use App\Entity\Traits\UpdatedAtTrait;
use DateTime;
use DateTimeInterface;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\HasLifecycleCallbacks]
#[ApiResource(
    operations: [
        new GetCollection(security: "is_granted('ROLE_ADMIN')"),
        new Get(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_STUDENT')"),
        new Post(security: "is_granted('ROLE_ADMIN')"),
        new Delete(security: "is_granted('ROLE_ADMIN')")
    ],
    normalizationContext: ['groups' => ['quiz_progress:read']],
    denormalizationContext: ['groups' => ['quiz_progress:write']]
)]
#[ORM\Entity]
class StudentQuizProgress
{
    use CreatedAtTrait, UpdatedAtTrait;

    #[ORM\Id]
    #[ORM\ManyToOne(targetEntity: User::class, inversedBy: 'quizProgresses')]
    #[ORM\JoinColumn(nullable: false)]
    #[Groups(['quiz_progress:read'])]
    private User $student;

    #[ORM\Id]
    #[ORM\ManyToOne(targetEntity: CourseQuiz::class)]
    #[ORM\JoinColumn(nullable: false)]
    #[Groups(['quiz_progress:read', 'quiz_progress:write'])]
    private CourseQuiz $quiz;

    #[ORM\Column(type: 'boolean')]
    #[Groups(['quiz_progress:read', 'quiz_progress:write'])]
    private bool $isCompleted = false;

    #[ORM\Column(type: 'integer', nullable: true)]
    #[Groups(['quiz_progress:read', 'quiz_progress:write'])]
    private ?int $score = null;

    #[ORM\Column(type: 'integer', nullable: true)]
    #[Groups(['quiz_progress:read'])]
    private ?int $correctAnswers = null;

    #[ORM\Column(type: 'integer', nullable: true)]
    #[Groups(['quiz_progress:read'])]
    private ?int $totalQuestions = null;

    #[ORM\Column(type: 'datetime', nullable: true)]
    #[Groups(['quiz_progress:read'])]
    private ?DateTimeInterface $completedAt = null;

    public function getStudent(): User
    {
        return $this->student;
    }

    public function setStudent(User $student): self
    {
        $this->student = $student;
        return $this;
    }

    public function getQuiz(): CourseQuiz
    {
        return $this->quiz;
    }

    public function setQuiz(CourseQuiz $quiz): self
    {
        $this->quiz = $quiz;
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

    public function getScore(): ?int
    {
        return $this->score;
    }

    public function setScore(?int $score): self
    {
        $this->score = $score;
        return $this;
    }

    public function getCorrectAnswers(): ?int
    {
        return $this->correctAnswers;
    }

    public function setCorrectAnswers(?int $correctAnswers): self
    {
        $this->correctAnswers = $correctAnswers;
        return $this;
    }

    public function getTotalQuestions(): ?int
    {
        return $this->totalQuestions;
    }

    public function setTotalQuestions(?int $totalQuestions): self
    {
        $this->totalQuestions = $totalQuestions;
        return $this;
    }

    public function getCompletedAt(): ?DateTimeInterface
    {
        return $this->completedAt;
    }
}
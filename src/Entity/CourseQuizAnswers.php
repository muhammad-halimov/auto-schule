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
use App\Repository\CourseQuizAnswersRepository;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\HasLifecycleCallbacks]
#[ORM\Table(name: 'course_quiz_answers')]
#[ORM\Entity(repositoryClass: CourseQuizAnswersRepository::class)]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Post(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_TEACHER')"),
        new Patch(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_TEACHER') or is_granted('ROLE_STUDENT')"),
        new Delete(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_TEACHER')"),
    ],
    normalizationContext: ['groups' => ['course_quiz_answers:read']],
    paginationEnabled: false,
)]
class CourseQuizAnswers
{
    use UpdatedAtTrait, CreatedAtTrait;

    public function __toString(): string
    {
        return "$this->answerText" ?? 'Без ответа';
    }

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups([
        'course_quiz_answers:read',
        'course_quizes:read',
        'courses:read'
    ])]
    private ?int $id = null;

    #[ORM\Column(type: Types::TEXT)]
    #[Groups([
        'course_quiz_answers:read',
        'course_quizes:read',
        'courses:read'
    ])]
    private ?string $answerText = null;

    #[ORM\Column]
    #[Groups([
        'course_quiz_answers:read',
        'course_quizes:read',
        'courses:read'
    ])]
    private ?bool $status = null;

    #[ORM\ManyToOne(cascade: ['all'], inversedBy: 'answers')]
    #[Groups([
        'course_quiz_answers:read',
        'course_quizes:read'
    ])]
    private ?CourseQuiz $courseQuiz = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getAnswerText(): ?string
    {
        return strip_tags($this->answerText);
    }

    public function setAnswerText(string $answerText): static
    {
        $this->answerText = $answerText;

        return $this;
    }

    public function isStatus(): ?bool
    {
        return $this->status;
    }

    public function setStatus(bool $status): static
    {
        $this->status = $status;

        return $this;
    }

    public function getCourseQuiz(): ?CourseQuiz
    {
        return $this->courseQuiz;
    }

    public function setCourseQuiz(?CourseQuiz $courseQuiz): static
    {
        $this->courseQuiz = $courseQuiz;

        return $this;
    }
}

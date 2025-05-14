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
use App\Repository\CourseQuizRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\HasLifecycleCallbacks]
#[ORM\Table(name: 'course_quiz')]
#[ORM\Entity(repositoryClass: CourseQuizRepository::class)]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Post(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_TEACHER')"),
        new Patch(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_TEACHER') or is_granted('ROLE_STUDENT')"),
        new Delete(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_TEACHER')"),
    ],
    normalizationContext: ['groups' => ['course_quizes:read']],
    paginationEnabled: false,
)]
class CourseQuiz
{
    use UpdatedAtTrait, CreatedAtTrait;

    public function __toString(): string
    {
        return "$this->question" ?? 'Без вопроса';
    }

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups([
        'course_quizes:read',
        'courses:read',
        'course_quiz_answers:read',
        'students:read'
    ])]
    private ?int $id = null;

    #[ORM\ManyToOne(cascade: ['all'], inversedBy: 'courseQuizzes')]
    #[Groups([
        'course_quizes:read',
        'course_quiz_answers:read',
    ])]
    private ?Course $course = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups([
        'course_quizes:read',
        'courses:read',
        'course_quiz_answers:read',
        'students:read'
    ])]
    private ?string $question = null;

    /**
     * @var Collection<int, CourseQuizAnswers>
     */
    #[ORM\OneToMany(mappedBy: 'courseQuiz', targetEntity: CourseQuizAnswers::class, cascade: ['all'])]
    #[Groups([
        'course_quizes:read',
        'courses:read',
        'students:read'
    ])]
    private Collection $answers;

    #[ORM\Column(type: 'integer', nullable: true)]
    #[Groups([
        'course_quizes:read',
        'courses:read',
        'students:read'
    ])]
    private ?int $orderNumber = null;

    public function __construct()
    {
        $this->answers = new ArrayCollection();
    }

    public function getId(): ?int
    {
        return $this->id;
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

    public function getQuestion(): ?string
    {
        return $this->question;
    }

    public function setQuestion(?string $question): static
    {
        $this->question = $question;

        return $this;
    }

    /**
     * @return Collection<int, CourseQuizAnswers>
     */
    public function getAnswers(): Collection
    {
        return $this->answers;
    }

    public function addAnswer(CourseQuizAnswers $answer): static
    {
        if (!$this->answers->contains($answer)) {
            $this->answers->add($answer);
            $answer->setCourseQuiz($this);
        }

        return $this;
    }

    public function removeAnswer(CourseQuizAnswers $answer): static
    {
        if ($this->answers->removeElement($answer)) {
            // set the owning side to null (unless already changed)
            if ($answer->getCourseQuiz() === $this) {
                $answer->setCourseQuiz(null);
            }
        }

        return $this;
    }

    public function getOrderNumber(): ?int
    {
        return $this->orderNumber;
    }

    public function setOrderNumber(?int $orderNumber): CourseQuiz
    {
        $this->orderNumber = $orderNumber;
        return $this;
    }
}

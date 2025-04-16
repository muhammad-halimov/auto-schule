<?php

namespace App\Entity;

use ApiPlatform\Metadata\ApiResource;
use ApiPlatform\Metadata\Get;
use ApiPlatform\Metadata\GetCollection;
use ApiPlatform\Metadata\Patch;
use ApiPlatform\Metadata\Post;
use App\Entity\Traits\CreatedAtTrait;
use App\Entity\Traits\UpdatedAtTrait;
use App\Repository\TeacherLessonRepository;
use DateTimeInterface;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\Entity(repositoryClass: TeacherLessonRepository::class)]
#[ORM\Table(name: 'teacherLesson')]
#[OrM\HasLifecycleCallbacks]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Post(security: "is_granted('ROLE_TEACHER') or is_granted('ROLE_ADMIN')"),
        new Patch(security: "is_granted('ROLE_TEACHER') or is_granted('ROLE_ADMIN')"),
    ],
    normalizationContext: ['groups' => ['teacherLessons:read']],
    paginationEnabled: false,
)]
class TeacherLesson
{
    use UpdatedAtTrait, CreatedAtTrait;

    public function __construct()
    {
        $this->studentProgresses = new ArrayCollection();
    }

    public function __toString()
    {
        return $this->title ?? 'Без названия';
    }

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups(['courses:read', 'students:read', 'teachers:read', 'teacherLessons:read'])]
    private ?int $id = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['courses:read', 'students:read', 'teachers:read', 'teacherLessons:read'])]
    private ?string $title = null;

    #[ORM\ManyToOne(inversedBy: 'teacherLesson')]
    #[ORM\JoinColumn(name: "teacher_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    private ?User $teacher = null;

    #[ORM\Column(type: Types::DATETIME_MUTABLE, nullable: true)]
    #[Groups(['courses:read', 'students:read', 'teachers:read', 'teacherLessons:read'])]
    private ?DateTimeInterface $date = null;

    #[ORM\ManyToOne(inversedBy: 'lessons')]
    #[Groups(['teacherLessons:read'])]
    private ?Course $course = null;

    /**
     * @var Collection<int, StudentLessonProgress>
     */
    #[ORM\OneToMany(mappedBy: 'lesson', targetEntity: StudentLessonProgress::class, orphanRemoval: true)]
    private Collection $studentProgresses;


    public function getId(): ?int
    {
        return $this->id;
    }

    public function getTitle(): ?string
    {
        return $this->title;
    }

    public function setTitle(?string $title): static
    {
        $this->title = $title;

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

    public function getCourse(): ?Course
    {
        return $this->course;
    }

    public function setCourse(?Course $course): static
    {
        $this->course = $course;

        return $this;
    }

    public function getTeacher(): ?User
    {
        return $this->teacher;
    }

    public function setTeacher(?User $teacher): static
    {
        $this->teacher = $teacher;

        return $this;
    }

    /**
     * @return Collection<int, StudentLessonProgress>
     */
    public function getStudentProgresses(): Collection
    {
        return $this->studentProgresses;
    }

    public function addStudentProgresses(StudentLessonProgress $studentLessonProgress): static
    {
        if (!$this->studentProgresses->contains($studentLessonProgress)) {
            $this->studentProgresses->add($studentLessonProgress);
            $studentLessonProgress->setLesson($this);
        }

        return $this;
    }

    public function removeStudentProgresses(StudentLessonProgress $studentLessonProgress): static
    {
        if ($this->studentProgresses->removeElement($studentLessonProgress)) {
            // set the owning side to null (unless already changed)
            if ($studentLessonProgress->getLesson() === $this) {
                $studentLessonProgress->setLesson(null);
            }
        }

        return $this;
    }
}

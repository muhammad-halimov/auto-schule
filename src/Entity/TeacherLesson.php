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
        new Delete(security: "is_granted('ROLE_TEACHER') or is_granted('ROLE_ADMIN')"),
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
        $this->videos = new ArrayCollection();
    }

    public function __toString()
    {
        return "Урок №$this->orderNumber: $this->title" ?? 'Без названия';
    }

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups(['courses:read', 'students:read', 'teachers:read', 'teacherLessons:read'])]
    private ?int $id = null;

    #[ORM\Column(length: 64, nullable: true)]
    #[Groups(['courses:read', 'students:read', 'teachers:read', 'teacherLessons:read'])]
    private ?string $title = null;

    #[ORM\Column(type: 'text', nullable: true)]
    #[Groups(['courses:read', 'students:read', 'teachers:read', 'teacherLessons:read'])]
    private ?string $description = null;

    #[ORM\Column(length: 16, nullable: true)]
    #[Groups(['courses:read', 'students:read', 'teachers:read', 'teacherLessons:read'])]
    private ?string $type = null;


    #[ORM\ManyToOne(inversedBy: 'teacherLesson')]
    #[ORM\JoinColumn(name: "teacher_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups(['students:read', 'courses:read'])]
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

    /**
     * @var Collection<int, TeacherLessonVideo>
     */
    #[ORM\OneToMany(mappedBy: 'teacherLesson', targetEntity: TeacherLessonVideo::class, cascade: ['all'], orphanRemoval: true)]
    #[Groups(['teacherLessons:read', 'students:read', 'courses:read'])]
    private Collection $videos;

    #[ORM\Column(type: 'integer', length: 2 , nullable: true)]
    #[Groups(['courses:read', 'students:read', 'teachers:read', 'teacherLessons:read'])]
    private ?int $orderNumber = null;


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

    public function getDescription(): ?string
    {
        return strip_tags($this->description);
    }

    public function setDescription(?string $description): static
    {
        $this->description = $description;

        return $this;
    }

    public function getType(): ?string
    {
        return $this->type;
    }

    public function setType(?string $type): static
    {
        $this->type = $type;

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

    public function getOrderNumber(): ?int
    {
        return $this->orderNumber;
    }

    public function setOrderNumber(?int $orderNumber): static
    {
        $this->orderNumber = $orderNumber;

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
                /** @noinspection PhpParamsInspection */
                $studentLessonProgress->setLesson(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, TeacherLessonVideo>
     */
    public function getVideos(): Collection
    {
        return $this->videos;
    }

    public function addVideo(TeacherLessonVideo $video): static
    {
        if (!$this->videos->contains($video)) {
            $this->videos->add($video);
            $video->setTeacherLesson($this);
        }

        return $this;
    }

    public function removeVideo(TeacherLessonVideo $video): static
    {
        if ($this->videos->removeElement($video)) {
            // set the owning side to null (unless already changed)
            if ($video->getTeacherLesson() === $this) {
                $video->setTeacherLesson(null);
            }
        }

        return $this;
    }
}

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
use App\Repository\CourseRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\HasLifecycleCallbacks]
#[ORM\Table(name: 'course')]
#[ORM\Entity(repositoryClass: CourseRepository::class)]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Post(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_TEACHER')"),
        new Patch(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_TEACHER') or is_granted('ROLE_STUDENT')"),
        new Delete(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_TEACHER')"),
    ],
    normalizationContext: ['groups' => ['courses:read']],
    paginationEnabled: false,
)]
class Course
{
    use UpdatedAtTrait, CreatedAtTrait;

    public function __construct()
    {
        $this->lessons = new ArrayCollection();
        $this->users = new ArrayCollection();
        $this->reviews = new ArrayCollection();
        $this->courseQuizzes = new ArrayCollection();
    }

    public function __toString() { return $this->title ?? 'Без названия'; }

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups([
        'courses:read',
        'students:read',
        'teacherLessons:read',
        'reviews:read',
        'course_quizes:read',
        'course_quiz_answers:read',
    ])]
    private ?int $id = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups([
        'courses:read',
        'students:read',
        'teacherLessons:read',
        'reviews:read',
        'course_quizes:read',
        'course_quiz_answers:read',
    ])]
    private ?string $title = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    #[Groups(['courses:read', 'students:read'])]
    private ?string $description = null;

    /**
     * @var Collection<int, TeacherLesson>
     */
    #[ORM\OneToMany(mappedBy: 'course', targetEntity: TeacherLesson::class, cascade: ['all'], orphanRemoval: true)]
    #[Groups(['courses:read', 'students:read'])]
    private Collection $lessons;

    /**
     * @var Collection<int, User>
     */
    #[ORM\ManyToMany(targetEntity: User::class, mappedBy: 'courses')]
    #[Groups(['courses:read'])]
    private Collection $users;

    #[ORM\ManyToOne(inversedBy: 'courses')]
    #[Groups(['courses:read', 'students:read'])]
    private ?Category $category = null;

    /**
     * @var Collection<int, Review>
     */
    #[ORM\OneToMany(mappedBy: 'course', targetEntity: Review::class)]
    private Collection $reviews;

    #[ORM\Column(type: 'integer', nullable: true)]
    #[Groups(['courses:read', 'students:read', 'teacherLessons:read'])]
    private ?int $price = null;

    /**
     * @var Collection<int, CourseQuiz>
     */
    #[ORM\OneToMany(mappedBy: 'course', targetEntity: CourseQuiz::class, cascade: ['all'])]
    #[ORM\JoinColumn(name: "course_quizzes_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups(['courses:read', 'students:read'])]
    private Collection $courseQuizzes;

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

    public function setDescription(?string $description): Course
    {
        $this->description = $description;
        return $this;
    }

    /**
     * @return Collection<int, TeacherLesson>
     */
    public function getLessons(): Collection
    {
        return $this->lessons;
    }

    public function addLesson(TeacherLesson $lesson): static
    {
        if (!$this->lessons->contains($lesson)) {
            $this->lessons->add($lesson);
            $lesson->setCourse($this);
        }

        return $this;
    }

    public function removeLesson(TeacherLesson $lesson): static
    {
        if ($this->lessons->removeElement($lesson)) {
            // set the owning side to null (unless already changed)
            if ($lesson->getCourse() === $this) {
                $lesson->setCourse(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, User>
     */
    public function getUsers(): Collection
    {
        return $this->users;
    }

    public function addUser(User $user): static
    {
        if (!$this->users->contains($user)) {
            $this->users->add($user);
            $user->addCourse($this);
        }

        return $this;
    }

    public function removeUser(User $user): static
    {
        if ($this->users->removeElement($user)) {
            $user->removeCourse($this);
        }

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

    /**
     * @return Collection<int, Review>
     */
    public function getReviews(): Collection
    {
        return $this->reviews;
    }

    public function addReview(Review $review): static
    {
        if (!$this->reviews->contains($review)) {
            $this->reviews->add($review);
            $review->setCourse($this);
        }

        return $this;
    }

    public function removeReview(Review $review): static
    {
        if ($this->reviews->removeElement($review)) {
            // set the owning side to null (unless already changed)
            if ($review->getCourse() === $this) {
                $review->setCourse(null);
            }
        }

        return $this;
    }

    public function getPrice(): ?int
    {
        return $this->price;
    }

    public function setPrice(?int $price): Course
    {
        $this->price = $price;
        return $this;
    }

    /**
     * @return Collection<int, CourseQuiz>
     */
    public function getCourseQuizzes(): Collection
    {
        return $this->courseQuizzes;
    }

    public function addCourseQuiz(CourseQuiz $courseQuiz): static
    {
        if (!$this->courseQuizzes->contains($courseQuiz)) {
            $this->courseQuizzes->add($courseQuiz);
            $courseQuiz->setCourse($this);
        }

        return $this;
    }

    public function removeCourseQuiz(CourseQuiz $courseQuiz): static
    {
        if ($this->courseQuizzes->removeElement($courseQuiz)) {
            // set the owning side to null (unless already changed)
            if ($courseQuiz->getCourse() === $this) {
                $courseQuiz->setCourse(null);
            }
        }

        return $this;
    }
}

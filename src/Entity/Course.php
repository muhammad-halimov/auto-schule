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
        $this->transactions = new ArrayCollection();
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
        'transactions:read'
    ])]
    private ?int $id = null;

    #[ORM\Column(length: 32, nullable: true)]
    #[Groups([
        'courses:read',
        'students:read',
        'teacherLessons:read',
        'reviews:read',
        'course_quizes:read',
        'course_quiz_answers:read',
        'transactions:read'
    ])]
    private ?string $title = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    #[Groups([
        'courses:read',
        'students:read',
        'transactions:read'
    ])]
    private ?string $description = null;

    /**
     * @var Collection<int, TeacherLesson>
     */
    #[ORM\OneToMany(mappedBy: 'course', targetEntity: TeacherLesson::class, orphanRemoval: true)]
    #[Groups([
        'courses:read',
        'students:read',
    ])]
    private Collection $lessons;

    /**
     * @var Collection<int, User>
     */
    #[ORM\ManyToMany(targetEntity: User::class, mappedBy: 'courses')]
    #[ORM\JoinColumn(name: "users_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups(['courses:read'])]
    private Collection $users;

    #[ORM\ManyToOne(cascade: ['all'], inversedBy: 'courses')]
    #[ORM\JoinColumn(name: "category_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups([
        'courses:read',
        'students:read',
        'transactions:read'
    ])]
    private ?Category $category = null;

    /**
     * @var Collection<int, Review>
     */
    #[ORM\OneToMany(mappedBy: 'course', targetEntity: Review::class)]
    private Collection $reviews;

    /**
     * @var Collection<int, CourseQuiz>
     */
    #[ORM\OneToMany(mappedBy: 'course', targetEntity: CourseQuiz::class)]
    #[ORM\JoinColumn(name: "course_quizzes_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups([
        'courses:read',
        'students:read',
    ])]
    private Collection $courseQuizzes;

    /**
     * @var Collection<int, Transaction>
     */
    #[ORM\OneToMany(mappedBy: 'course', targetEntity: Transaction::class)]
    #[ORM\JoinColumn(name: "transactions_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    private Collection $transactions;

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

    #[Groups([
        'transactions:read'
    ])]
    public function getLessonsCount(): int
    {
        return $this->lessons->count();
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

    /**
     * @return Collection<int, CourseQuiz>
     */
    public function getCourseQuizzes(): Collection
    {
        return $this->courseQuizzes;
    }

    #[Groups([
        'transactions:read'
    ])]
    public function getCourseQuizzesCount(): int
    {
        return $this->courseQuizzes->count();
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

    /**
     * @return Collection<int, Transaction>
     */
    public function getTransactions(): Collection
    {
        return $this->transactions;
    }

    public function addTransaction(Transaction $transaction): static
    {
        if (!$this->transactions->contains($transaction)) {
            $this->transactions->add($transaction);
            $transaction->setCourse($this);
        }

        return $this;
    }

    public function removeTransaction(Transaction $transaction): static
    {
        if ($this->transactions->removeElement($transaction)) {
            // set the owning side to null (unless already changed)
            if ($transaction->getCourse() === $this) {
                $transaction->setCourse(null);
            }
        }

        return $this;
    }
}

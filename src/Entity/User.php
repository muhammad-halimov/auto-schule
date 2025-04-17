<?php

namespace App\Entity;

use ApiPlatform\Metadata\ApiResource;
use ApiPlatform\Metadata\Get;
use ApiPlatform\Metadata\GetCollection;
use ApiPlatform\Metadata\Patch;
use ApiPlatform\Metadata\Post;
use App\Controller\Api\Filter\AdminFilterController;
use App\Controller\Api\Filter\InstructorFilterController;
use App\Controller\Api\Filter\SingleStudentFilterController;
use App\Controller\Api\Filter\StudentFilterController;
use App\Controller\Api\Filter\TeacherFilterController;
use App\Entity\Traits\CreatedAtTrait;
use App\Entity\Traits\UpdatedAtTrait;
use App\Repository\UserRepository;
use DateTime;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\HttpFoundation\File\File;
use Symfony\Component\Security\Core\User\PasswordAuthenticatedUserInterface;
use Symfony\Component\Security\Core\User\UserInterface;
use Symfony\Component\Serializer\Annotation\Groups;
use Symfony\Component\Serializer\Annotation\SerializedName;
use Symfony\Component\Validator\Constraints as Assert;
use Vich\UploaderBundle\Mapping\Annotation as Vich;

#[ORM\Entity(repositoryClass: UserRepository::class)]
#[ORM\Table(name: 'user')]
#[ORM\HasLifecycleCallbacks]
#[Vich\Uploadable]
#[ApiResource(
    operations: [
        new Get(),
        new Get(uriTemplate: '/students/{id}', controller: SingleStudentFilterController::class),
        new GetCollection(),
        new GetCollection(uriTemplate: '/teachers', controller: TeacherFilterController::class),
        new GetCollection(uriTemplate: '/instructors', controller: InstructorFilterController::class),
        new GetCollection(uriTemplate: '/students', controller: StudentFilterController::class),
        new GetCollection(uriTemplate: '/admins', controller: AdminFilterController::class),
        new Post(),
        new Patch(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_STUDENT')"),
    ],
    normalizationContext: ['groups' => [
        'admins:read',
        'students:read',
        'teachers:read',
        'instructors:read',
    ]],
    paginationEnabled: false,
)]
class User implements UserInterface, PasswordAuthenticatedUserInterface
{
    use UpdatedAtTrait, CreatedAtTrait;

    public function __construct()
    {
        $this->reviews = new ArrayCollection();
        $this->teacherLesson = new ArrayCollection();
        $this->instructorLesson = new ArrayCollection();
        $this->instructorLessonStudent = new ArrayCollection();
        $this->courses = new ArrayCollection();
        $this->lessonProgresses = new ArrayCollection();
    }

    public function __toString()
    {
        return $this->email ?? 'Без почты';
    }

    public const ROLES = [
        'Администратор' => 'ROLE_ADMIN',
        'Студент' => 'ROLE_STUDENT',
        'Инструктор' => 'ROLE_INSTRUCTOR',
        'Преподаватель' => 'ROLE_TEACHER',
    ];

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: 'integer', nullable: false)]
    #[Groups(['students:read', 'teachers:read', 'instructors:read', 'admins:read'])]
    private ?int $id = null;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['students:read', 'teachers:read', 'instructors:read', 'admins:read', 'reviews:read'])]
    private ?string $username = null;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['students:read', 'teachers:read', 'instructors:read', 'admins:read', 'reviews:read'])]
    private ?string $name = null;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['students:read', 'teachers:read', 'instructors:read', 'admins:read', 'reviews:read'])]
    private ?string $surname = null;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['students:read', 'teachers:read', 'instructors:read', 'admins:read'])]
    private ?string $patronym = null;

    #[ORM\Column(type: 'string', length: 15, nullable: true)]
    #[Groups(['students:read', 'teachers:read', 'instructors:read', 'admins:read'])]
    private ?string $phone = null;

    #[ORM\Column(type: 'string', length: 255, unique: true)]
    #[Groups(['students:read', 'teachers:read', 'instructors:read', 'admins:read', 'reviews:read'])]
    private ?string $email = null;

    #[ORM\Column(type: 'datetime', nullable: true)]
    #[Groups(['students:read', 'teachers:read', 'instructors:read', 'admins:read'])]
    private ?DateTime $dateOfBirth = null;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['students:read'])]
    private ?string $contract = null;

    #[ORM\Column(type: 'boolean', nullable: true)]
    #[Groups(['students:read'])]
    private ?bool $examStatus = null;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['instructors:read', 'teachers:read'])]
    private ?string $license = null;

    #[ORM\Column(type: 'string', length: 255, nullable: true)]
    #[Groups(['teachers:read'])]
    private ?string $classTitle = null;

    #[ORM\Column(type: 'datetime', nullable: true)]
    #[Groups(['teachers:read', 'instructors:read'])]
    private ?DateTime $hireDate = null;

    #[ORM\Column(type: 'datetime', nullable: true)]
    #[Groups(['students:read'])]
    private ?DateTime $enrollDate = null;

    #[ORM\OneToMany(mappedBy: 'teacher', targetEntity: TeacherLesson::class)]
    private Collection $teacherLesson;

    #[ORM\OneToMany(mappedBy: 'instructor', targetEntity: InstructorLesson::class)]
    private Collection $instructorLesson;

    #[ORM\OneToMany(mappedBy: 'student', targetEntity: InstructorLesson::class)]
    private Collection $instructorLessonStudent;

    #[ORM\Column(type: 'json')]
    #[Groups(['teachers:read', 'instructors:read', 'admins:read', 'students:read'])]
    private array $roles = [];

    #[ORM\Column(type: 'boolean', nullable: true)]
    #[Groups(['teachers:read', 'instructors:read', 'admins:read', 'students:read'])]
    #[SerializedName('is_active')]
    private ?bool $isActive = false;

    #[ORM\Column(type: 'boolean', nullable: true)]
    #[Groups(['teachers:read', 'instructors:read', 'admins:read', 'students:read'])]
    #[SerializedName('is_approved')]
    private ?bool $isApproved = false;

    #[ORM\Column(type: 'text', nullable: true)]
    private ?string $message = null;

    #[ORM\ManyToOne(inversedBy: 'students')]
    #[ORM\JoinColumn(name: "exam_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups(['students:read'])]
    private ?Exam $exam = null;

    /**
     * @var Collection<int, Review>
     */
    #[ORM\OneToMany(mappedBy: 'publisher', targetEntity: Review::class)]
    #[Groups(['students:read'])]
    private Collection $reviews;

    /**
     * @var Collection<int, Course>
     */
    #[ORM\ManyToMany(targetEntity: Course::class, inversedBy: 'users')]
    #[Groups(['students:read'])]
    private Collection $courses;

    #[ORM\ManyToOne(inversedBy: 'users')]
    #[Groups(['instructors:read'])]
    private ?Car $car = null;

    /**
     * @var Collection<int, StudentLessonProgress>
     */
    #[ORM\OneToMany(mappedBy: 'student', targetEntity: StudentLessonProgress::class, cascade: ['persist'], orphanRemoval: true)]
    private Collection $lessonProgresses;

    #[Vich\UploadableField(mapping: 'profile_photos', fileNameProperty: 'image')]
    #[Assert\Image(mimeTypes: ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'])]
    private ?File $imageFile = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['instructors:read', 'teachers:read', 'admins:read', 'students:read'])]
    private ?string $image = null;

    #[ORM\Column(type: 'string', nullable: true)]
    private string $password;

    private ?string $plainPassword = null;

    /**
     * @return string|null
     */
    public function getPlainPassword(): ?string
    {
        return $this->plainPassword;
    }

    /**
     * @param string|null $plainPassword
     */
    public function setPlainPassword(?string $plainPassword): void
    {
        $this->plainPassword = $plainPassword;
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getUsername(): ?string
    {
        return $this->username;
    }

    public function setUsername(string $username): self
    {
        $this->username = $username;

        return $this;
    }

    public function getName(): ?string
    {
        return $this->name;
    }

    public function setName(?string $name): User
    {
        $this->name = $name;
        return $this;
    }

    public function getSurname(): ?string
    {
        return $this->surname;
    }

    public function setSurname(?string $surname): User
    {
        $this->surname = $surname;
        return $this;
    }

    public function getPatronym(): ?string
    {
        return $this->patronym;
    }

    public function setPatronym(?string $patronym): User
    {
        $this->patronym = $patronym;
        return $this;
    }

    public function getPhone(): ?string
    {
        return $this->phone;
    }

    public function setPhone(?string $phone): User
    {
        $this->phone = $phone;
        return $this;
    }

    public function getEmail(): ?string
    {
        return $this->email;
    }

    public function setEmail(?string $email): User
    {
        $this->email = $email;
        return $this;
    }

    public function getDateOfBirth(): ?DateTime
    {
        return $this->dateOfBirth;
    }

    public function setDateOfBirth(?DateTime $dateOfBirth): User
    {
        $this->dateOfBirth = $dateOfBirth;
        return $this;
    }

    public function getContract(): ?string
    {
        return $this->contract;
    }

    public function setContract(?string $contract): User
    {
        $this->contract = $contract;
        return $this;
    }

    public function getExamStatus(): ?bool
    {
        return $this->examStatus;
    }

    public function setExamStatus(?bool $examStatus): User
    {
        $this->examStatus = $examStatus;
        return $this;
    }

    public function getLicense(): ?string
    {
        return $this->license;
    }

    public function setLicense(?string $license): User
    {
        $this->license = $license;
        return $this;
    }

    public function getClassTitle(): ?string
    {
        return $this->classTitle;
    }

    public function setClassTitle(?string $classTitle): User
    {
        $this->classTitle = $classTitle;
        return $this;
    }

    public function getHireDate(): ?DateTime
    {
        return $this->hireDate;
    }

    public function setHireDate(?DateTime $hireDate): User
    {
        $this->hireDate = $hireDate;
        return $this;
    }

    public function getEnrollDate(): ?DateTime
    {
        return $this->enrollDate;
    }

    public function setEnrollDate(?DateTime $enrollDate): User
    {
        $this->enrollDate = $enrollDate;
        return $this;
    }

    public function getExam(): ?Exam
    {
        return $this->exam;
    }

    public function setExam(?Exam $exam): static
    {
        $this->exam = $exam;

        return $this;
    }

    public function getIsActive(): ?bool
    {
        return $this->isActive;
    }

    public function setIsActive(?bool $is_active): static
    {
        $this->isActive = $is_active;
        return $this;
    }

    public function getIsApproved(): ?bool
    {
        return $this->isApproved;
    }

    public function setIsApproved(?bool $is_approved): static
    {
        $this->isApproved = $is_approved;
        return $this;
    }

    public function getMessage(): ?string
    {
        return $this->message;
    }

    public function setMessage(?string $message): static
    {
        $this->message = $message;
        return $this;
    }

    /**
     * A visual identifier that represents this user.
     *
     * @see UserInterface
     */
    public function getUserIdentifier(): string
    {
        return (string)$this->email;
    }

    /**
     * @see UserInterface
     */
    public function getRoles(): array
    {
        $roles = $this->roles;
        // guarantee every user at least has ROLE_USER
        $roles[] = 'ROLE_USER';

        return array_unique($roles);
    }

    public function setRoles(array $roles): self
    {
        $this->roles = $roles;

        return $this;
    }

    /**
     * @see PasswordAuthenticatedUserInterface
     */
    public function getPassword(): string
    {
        return $this->password;
    }

    public function setPassword(string $password): self
    {
        $this->password = $password;

        return $this;
    }

    /**
     * @see UserInterface
     */
    public function eraseCredentials(): void
    {
        // If you store any temporary, sensitive data on the user, clear it here
        // $this->plainPassword = null;
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
            $review->setPublisher($this);
        }

        return $this;
    }

    public function removeReview(Review $review): static
    {
        if ($this->reviews->removeElement($review)) {
            // set the owning side to null (unless already changed)
            if ($review->getPublisher() === $this) {
                $review->setPublisher(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, TeacherLesson>
     */
    public function getTeacherLesson(): Collection
    {
        return $this->teacherLesson;
    }

    public function addTeacherLesson(TeacherLesson $teacherLesson): static
    {
        if (!$this->teacherLesson->contains($teacherLesson)) {
            $this->teacherLesson->add($teacherLesson);
            $teacherLesson->setTeacher($this);
        }

        return $this;
    }

    public function removeTeacherLesson(TeacherLesson $teacherLesson): static
    {
        if ($this->teacherLesson->removeElement($teacherLesson)) {
            // set the owning side to null (unless already changed)
            if ($teacherLesson->getTeacher() === $this) {
                $teacherLesson->setTeacher(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, InstructorLesson>
     */
    public function getInstructorLesson(): Collection
    {
        return $this->instructorLesson;
    }

    public function addInstructorLesson(InstructorLesson $instructorLesson): static
    {
        if (!$this->instructorLesson->contains($instructorLesson)) {
            $this->instructorLesson->add($instructorLesson);
            $instructorLesson->setInstructor($this);
        }

        return $this;
    }

    public function removeInstructorLesson(InstructorLesson $instructorLesson): static
    {
        if ($this->instructorLesson->removeElement($instructorLesson)) {
            // set the owning side to null (unless already changed)
            if ($instructorLesson->getInstructor() === $this) {
                $instructorLesson->setInstructor(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, InstructorLesson>
     */
    public function getInstructorLessonStudent(): Collection
    {
        return $this->instructorLessonStudent;
    }

    public function addInstructorLessonStudent(InstructorLesson $instructorLessonStudent): static
    {
        if (!$this->instructorLessonStudent->contains($instructorLessonStudent)) {
            $this->instructorLessonStudent->add($instructorLessonStudent);
            $instructorLessonStudent->setStudent($this);
        }

        return $this;
    }

    public function removeInstructorLessonStudent(InstructorLesson $instructorLessonStudent): static
    {
        if ($this->instructorLessonStudent->removeElement($instructorLessonStudent)) {
            // set the owning side to null (unless already changed)
            if ($instructorLessonStudent->getStudent() === $this) {
                $instructorLessonStudent->setStudent(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, Course>
     */
    public function getCourses(): Collection
    {
        return $this->courses;
    }

    public function addCourse(Course $course): static
    {
        if (!$this->courses->contains($course)) {
            $this->courses->add($course);
        }

        return $this;
    }

    public function removeCourse(Course $course): static
    {
        $this->courses->removeElement($course);

        return $this;
    }

    /**
     * @return Collection
     */
    public function getLessonProgresses(): Collection
    {
        return $this->lessonProgresses;
    }

    public function getProgress(): array
    {
        dump($this->courses->map(fn($c) => [
            'id' => $c->getId(),
            'title' => $c->getTitle(),
            'lessonCount' => $c->getLessons()->count()
        ])->toArray());

        $courseProgress = [];
        $totalStats = [
            'completed' => 0,
            'total' => 0,
            'percentage' => 0
        ];

        // Guard clause for no courses
        if ($this->courses->isEmpty()) {
            return [
                'byCourse' => [],
                'overall' => $totalStats
            ];
        }

        foreach ($this->courses as $course) {
            if (!$course) {
                continue; // Skip null courses
            }

            $courseId = $course->getId();
            $lessons = $course->getLessons();

            // Initialize course progress data
            $courseProgress[$courseId] = [
                'courseId' => $courseId,
                'courseTitle' => $course->getTitle() ?? 'Untitled Course',
                'completed' => 0,
                'total' => count($lessons),
                'percentage' => 0
            ];

            // Count completed lessons
            foreach ($lessons as $lesson) {
                if (!$lesson) {
                    continue; // Skip null lessons
                }

                $progress = $this->getLessonProgress($lesson);
                if ($progress && $progress->isCompleted()) {
                    $courseProgress[$courseId]['completed']++;
                }
            }

            // Calculate course percentage
            if ($courseProgress[$courseId]['total'] > 0) {
                $courseProgress[$courseId]['percentage'] = (int) round(
                    ($courseProgress[$courseId]['completed'] / $courseProgress[$courseId]['total']) * 100
                );
            }

            // Update overall stats
            $totalStats['completed'] += $courseProgress[$courseId]['completed'];
            $totalStats['total'] += $courseProgress[$courseId]['total'];
        }

        // Calculate overall percentage
        if ($totalStats['total'] > 0) {
            $totalStats['percentage'] = (int) round(
                ($totalStats['completed'] / $totalStats['total']) * 100
            );
        }

        return [
            'byCourse' => array_values($courseProgress), // Convert to indexed array
            'overall' => $totalStats
        ];
    }

    public function getLessonProgress(TeacherLesson $lesson): ?StudentLessonProgress
    {
        foreach ($this->lessonProgresses as $progress) {
            if ($progress->getLesson() === $lesson) {
                return $progress;
            }
        }
        return null;
    }

    public function markLessonCompleted(TeacherLesson $lesson): void
    {
        $progress = $this->getLessonProgress($lesson);
        if (!$progress) {
            $progress = new StudentLessonProgress();
            $progress->setStudent($this);
            $progress->setLesson($lesson);
            $this->lessonProgresses->add($progress);
        }

        $progress->setIsCompleted(true);
    }

    public function getCar(): ?Car
    {
        return $this->car;
    }

    public function setCar(?Car $car): static
    {
        $this->car = $car;

        return $this;
    }

    public function getImage(): ?string
    {
        return $this->image;
    }

    public function setImage(?string $image): static
    {
        $this->image = $image;

        return $this;
    }

    public function getImageFile(): ?File
    {
        return $this->imageFile;
    }

    public function setImageFile(?File $imageFile): self
    {
        $this->imageFile = $imageFile;
        if (null !== $imageFile) {
            $this->updatedAt = new DateTime();
        }

        return $this;
    }
}

<?php

namespace App\Entity;

use ApiPlatform\Metadata\ApiResource;
use ApiPlatform\Metadata\Get;
use ApiPlatform\Metadata\GetCollection;
use ApiPlatform\Metadata\Patch;
use ApiPlatform\Metadata\Post;
use App\Entity\Traits\CreatedAtTrait;
use App\Entity\Traits\UpdatedAtTrait;
use App\Repository\CategoryRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Attribute\Groups;

#[ORM\HasLifecycleCallbacks]
#[ORM\Table(name: 'category')]
#[ORM\Entity(repositoryClass: CategoryRepository::class)]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Post(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_TEACHER') or is_granted('ROLE_INSTRUCTOR')"),
        new Patch(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_TEACHER') or is_granted('ROLE_INSTRUCTOR')"),
    ],
    normalizationContext: ['groups' => ['category:read']],
    paginationEnabled: false,
)]
class Category
{
    use UpdatedAtTrait, CreatedAtTrait;

    public function __construct()
    {
        $this->cars = new ArrayCollection();
        $this->courses = new ArrayCollection();
        $this->driveSchedules = new ArrayCollection();
        $this->instructorLessons = new ArrayCollection();
    }

    public function __toString()
    {
        return $this->title ?? 'Без названия';
    }

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups([
        'category:read',
        'exams:read',
        'course:read',
        'students:read',
        'prices:read',
        'instructorLessons:read',
        'driveSchedule:read'
    ])]
    private ?int $id = null;

    #[ORM\Column(type: Types::STRING, nullable: true)]
    #[Groups([
        'category:read',
        'exams:read',
        'course:read',
        'students:read',
        'prices:read',
        'instructorLessons:read',
        'driveSchedule:read'
    ])]
    private ?string $title = null;

    #[ORM\ManyToOne(inversedBy: 'categories')]
    #[ORM\JoinColumn(name: "category_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    private ?Exam $category = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    #[Groups(['category:read', 'exams:read', 'course:read', 'students:read'])]
    private ?string $description = null;

    /**
     * @var Collection<int, Car>
     */
    #[ORM\OneToMany(mappedBy: 'category', targetEntity: Car::class)]
    private Collection $cars;

    /**
     * @var Collection<int, Course>
     */
    #[ORM\OneToMany(mappedBy: 'category', targetEntity: Course::class)]
    private Collection $courses;

    /**
     * @var Collection<int, DriveSchedule>
     */
    #[ORM\OneToMany(mappedBy: 'сcategory', targetEntity: DriveSchedule::class)]
    private Collection $driveSchedules;

    /**
     * @var Collection<int, InstructorLesson>
     */
    #[ORM\OneToMany(mappedBy: 'category', targetEntity: InstructorLesson::class)]
    private Collection $instructorLessons;

    #[ORM\OneToOne(mappedBy: 'category', cascade: ['persist', 'remove'])]
    #[Groups(['driveSchedule:read', 'instructorLessons:read'])]
    private ?Price $price = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getCategory(): ?Exam
    {
        return $this->category;
    }

    public function setCategory(?Exam $category): static
    {
        $this->category = $category;

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

    public function getTitle(): ?string
    {
        return $this->title;
    }

    public function setTitle(?string $title): static
    {
        $this->title = $title;
        return $this;
    }

    /**
     * @return Collection<int, Car>
     */
    public function getCars(): Collection
    {
        return $this->cars;
    }

    public function addCar(Car $car): static
    {
        if (!$this->cars->contains($car)) {
            $this->cars->add($car);
            $car->setCategory($this);
        }

        return $this;
    }

    public function removeCar(Car $car): static
    {
        if ($this->cars->removeElement($car)) {
            // set the owning side to null (unless already changed)
            if ($car->getCategory() === $this) {
                $car->setCategory(null);
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
            $course->setCategory($this);
        }

        return $this;
    }

    public function removeCourse(Course $course): static
    {
        if ($this->courses->removeElement($course)) {
            // set the owning side to null (unless already changed)
            if ($course->getCategory() === $this) {
                $course->setCategory(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, DriveSchedule>
     */
    public function getDriveSchedules(): Collection
    {
        return $this->driveSchedules;
    }

    public function addDriveSchedule(DriveSchedule $driveSchedule): static
    {
        if (!$this->driveSchedules->contains($driveSchedule)) {
            $this->driveSchedules->add($driveSchedule);
            $driveSchedule->setCategory($this);
        }

        return $this;
    }

    public function removeDriveSchedule(DriveSchedule $driveSchedule): static
    {
        if ($this->driveSchedules->removeElement($driveSchedule)) {
            // set the owning side to null (unless already changed)
            if ($driveSchedule->getCategory() === $this) {
                $driveSchedule->setCategory(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, InstructorLesson>
     */
    public function getInstructorLessons(): Collection
    {
        return $this->instructorLessons;
    }

    public function addInstructorLesson(InstructorLesson $instructorLesson): static
    {
        if (!$this->instructorLessons->contains($instructorLesson)) {
            $this->instructorLessons->add($instructorLesson);
            $instructorLesson->setCategory($this);
        }

        return $this;
    }

    public function removeInstructorLesson(InstructorLesson $instructorLesson): static
    {
        if ($this->instructorLessons->removeElement($instructorLesson)) {
            // set the owning side to null (unless already changed)
            if ($instructorLesson->getCategory() === $this) {
                $instructorLesson->setCategory(null);
            }
        }

        return $this;
    }

    public function getPrice(): ?Price
    {
        return $this->price;
    }

    public function setPrice(?Price $price): static
    {
        // unset the owning side of the relation if necessary
        if ($price === null && $this->price !== null) {
            $this->price->setCategory(null);
        }

        // set the owning side of the relation if necessary
        if ($price !== null && $price->getCategory() !== $this) {
            $price->setCategory($this);
        }

        $this->price = $price;

        return $this;
    }
}

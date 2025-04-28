<?php

namespace App\Entity;

use ApiPlatform\Metadata\ApiResource;
use ApiPlatform\Metadata\Get;
use ApiPlatform\Metadata\GetCollection;
use ApiPlatform\Metadata\Patch;
use ApiPlatform\Metadata\Post;
use App\Entity\Traits\CreatedAtTrait;
use App\Entity\Traits\UpdatedAtTrait;
use App\Repository\ExamRepository;
use DateTimeInterface;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\HasLifecycleCallbacks]
#[ORM\Table(name: 'exam')]
#[ORM\Entity(repositoryClass: ExamRepository::class)]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Post(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_INSTRUCTOR')"),
        new Patch(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_INSTRUCTOR')"),
    ],
    normalizationContext: ['groups' => ['exams:read']],
    paginationEnabled: false,
)]
class Exam
{
    use UpdatedAtTrait, CreatedAtTrait;

    public function __construct()
    {
        $this->students = new ArrayCollection();
        $this->categories = new ArrayCollection();
    }

    public function __toString()
    {
        return "ID: $this->id; Дата и время: {$this->date->format('d-m-Y H:i')}";
    }

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups(['exams:read', 'students:read'])]
    private ?int $id = null;

    #[ORM\Column(type: Types::DATETIME_MUTABLE, nullable: true)]
    #[Groups(['exams:read', 'students:read'])]
    private ?DateTimeInterface $date = null;

    /**
     * @var Collection<int, User>
     */
    #[ORM\OneToMany(mappedBy: 'exam', targetEntity: User::class)]
    private Collection $students;

    /**
     * @var Collection<int, Category>
     */
    #[ORM\OneToMany(mappedBy: 'category', targetEntity: Category::class)]
    #[Groups(['exams:read'])]
    private Collection $categories;

    #[ORM\ManyToOne(inversedBy: 'exams')]
    #[ORM\JoinColumn(name: "autodrome_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups(['exams:read'])]
    private ?Autodrome $autodrome = null;

    public function getId(): ?int
    {
        return $this->id;
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

    /**
     * @return Collection<int, User>
     */
    public function getStudents(): Collection
    {
        return $this->students;
    }

    public function addStudent(User $student): static
    {
        if (!$this->students->contains($student)) {
            $this->students->add($student);
            $student->setExam($this);
        }

        return $this;
    }

    public function removeStudent(User $student): static
    {
        if ($this->students->removeElement($student)) {
            // set the owning side to null (unless already changed)
            if ($student->getExam() === $this) {
                $student->setExam(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, Category>
     */
    public function getCategories(): Collection
    {
        return $this->categories;
    }

    public function addCategory(Category $category): static
    {
        if (!$this->categories->contains($category)) {
            $this->categories->add($category);
            $category->setCategory($this);
        }

        return $this;
    }

    public function removeCategory(Category $category): static
    {
        if ($this->categories->removeElement($category)) {
            // set the owning side to null (unless already changed)
            if ($category->getCategory() === $this) {
                $category->setCategory(null);
            }
        }

        return $this;
    }

    public function getAutodrome(): ?Autodrome
    {
        return $this->autodrome;
    }

    public function setAutodrome(?Autodrome $autodrome): static
    {
        $this->autodrome = $autodrome;

        return $this;
    }
}

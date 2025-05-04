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
use App\Repository\AutodromeRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\HasLifecycleCallbacks]
#[ORM\Table(name: 'autodrome')]
#[ORM\Entity(repositoryClass: AutodromeRepository::class)]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Post(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_INSTRUCTOR')"),
        new Patch(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_INSTRUCTOR')"),
        new Delete(security: "is_granted('ROLE_ADMIN')"),
    ],
    normalizationContext: ['groups' => ['autodromes:read']],
    paginationEnabled: false,
)]
class Autodrome
{
    use UpdatedAtTrait, CreatedAtTrait;

    public function __construct()
    {
        $this->exams = new ArrayCollection();
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
    #[Groups(['autodromes:read', 'exams:read', 'instructorLessons:read', 'driveSchedule:read'])]
    private ?int $id = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['autodromes:read', 'exams:read', 'instructorLessons:read', 'driveSchedule:read'])]
    private ?string $title = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['autodromes:read', 'exams:read'])]
    private ?string $address = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    #[Groups(['autodromes:read', 'exams:read'])]
    private ?string $description = null;

    /**
     * @var Collection<int, Exam>
     */
    #[ORM\OneToMany(mappedBy: 'autodrome', targetEntity: Exam::class, cascade: ['all'])]
    private Collection $exams;

    /**
     * @var Collection<int, DriveSchedule>
     */
    #[ORM\OneToMany(mappedBy: 'autodrome', targetEntity: DriveSchedule::class)]
    private Collection $driveSchedules;

    /**
     * @var Collection<int, InstructorLesson>
     */
    #[ORM\OneToMany(mappedBy: 'autodrome', targetEntity: InstructorLesson::class)]
    private Collection $instructorLessons;

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

    public function getAddress(): ?string
    {
        return $this->address;
    }

    public function setAddress(?string $address): static
    {
        $this->address = $address;
        return $this;
    }

    /**
     * @return Collection<int, Exam>
     */
    public function getExams(): Collection
    {
        return $this->exams;
    }

    public function addExam(Exam $exam): static
    {
        if (!$this->exams->contains($exam)) {
            $this->exams->add($exam);
            $exam->setAutodrome($this);
        }

        return $this;
    }

    public function removeExam(Exam $exam): static
    {
        if ($this->exams->removeElement($exam)) {
            // set the owning side to null (unless already changed)
            if ($exam->getAutodrome() === $this) {
                $exam->setAutodrome(null);
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
            $driveSchedule->setAutodrome($this);
        }

        return $this;
    }

    public function removeDriveSchedule(DriveSchedule $driveSchedule): static
    {
        if ($this->driveSchedules->removeElement($driveSchedule)) {
            // set the owning side to null (unless already changed)
            if ($driveSchedule->getAutodrome() === $this) {
                $driveSchedule->setAutodrome(null);
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
            $instructorLesson->setAutodrome($this);
        }

        return $this;
    }

    public function removeInstructorLesson(InstructorLesson $instructorLesson): static
    {
        if ($this->instructorLessons->removeElement($instructorLesson)) {
            // set the owning side to null (unless already changed)
            if ($instructorLesson->getAutodrome() === $this) {
                $instructorLesson->setAutodrome(null);
            }
        }

        return $this;
    }
}

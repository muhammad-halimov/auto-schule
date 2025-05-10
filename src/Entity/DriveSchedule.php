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
use App\Repository\DriveScheduleRepository;
use DateTimeInterface;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\HasLifecycleCallbacks]
#[ORM\Table(name: 'drive_schedule')]
#[ORM\Entity(repositoryClass: DriveScheduleRepository::class)]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Post(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_INSTRUCTOR')"),
        new Patch(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_INSTRUCTOR')"),
        new Delete(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_INSTRUCTOR')"),
    ],
    normalizationContext: ['groups' => ['driveSchedule:read']],
    paginationEnabled: false,
)]
class DriveSchedule
{
    use createdAtTrait, updatedAtTrait;

    public function __toString()
    {
        return
        "ID: $this->id; 
        Инструктор: $this->instructor; 
        Рабочие часы: {$this->timeFrom->format('H:i')} - {$this->timeTo->format('H:i')}; 
        Рабочие часы: $this->daysOfWeek";
    }

    public function __construct(){}

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups(['driveSchedule:read'])]
    private ?int $id = null;

    #[ORM\Column(type: Types::TIME_MUTABLE, nullable: true)]
    #[Groups(['driveSchedule:read'])]
    private ?DateTimeInterface $timeFrom = null;

    #[ORM\Column(type: Types::TIME_MUTABLE, nullable: true)]
    #[Groups(['driveSchedule:read'])]
    private ?DateTimeInterface $timeTo = null;

    #[ORM\Column(type: Types::STRING, nullable: true)]
    #[Groups(['driveSchedule:read'])]
    private ?string $daysOfWeek = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    #[Groups(['driveSchedule:read'])]
    private ?string $notice = null;

    #[ORM\ManyToOne(inversedBy: 'driveSchedules')]
    #[ORM\JoinColumn(name: "autodrome_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups(['driveSchedule:read'])]
    private ?Autodrome $autodrome = null;

    #[ORM\ManyToOne(inversedBy: 'driveSchedules')]
    #[ORM\JoinColumn(name: "category_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups(['driveSchedule:read'])]
    private ?Category $category = null;

    #[ORM\OneToOne(inversedBy: 'driveSchedule', cascade: ['persist', 'remove'])]
    #[ORM\JoinColumn(name: "instructor_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups(['driveSchedule:read'])]
    private ?User $instructor = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getTimeTo(): ?DateTimeInterface
    {
        return $this->timeTo;
    }

    public function setTimeTo(?DateTimeInterface $timeTo): DriveSchedule
    {
        $this->timeTo = $timeTo;
        return $this;
    }

    public function getTimeFrom(): ?DateTimeInterface
    {
        return $this->timeFrom;
    }

    public function setTimeFrom(?DateTimeInterface $timeFrom): static
    {
        $this->timeFrom = $timeFrom;

        return $this;
    }

    public function getNotice(): ?string
    {
        return strip_tags($this->notice);
    }

    public function setNotice(?string $notice): static
    {
        $this->notice = $notice;

        return $this;
    }

    public function setDaysOfWeek(array|string|null $daysOfWeek): self
    {
        is_array($daysOfWeek)
            ? $this->daysOfWeek = implode(',', $daysOfWeek)
            : $this->daysOfWeek = $daysOfWeek;

        return $this;
    }

    public function getDaysOfWeek(): array
    {
        if (empty($this->daysOfWeek)) return [];
        return explode(',', $this->daysOfWeek);
    }

    public function getDaysOfWeekString(): ?string
    {
        return $this->daysOfWeek;
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

    public function getCategory(): ?Category
    {
        return $this->category;
    }

    public function setCategory(?Category $category): static
    {
        $this->category = $category;

        return $this;
    }

    public function getInstructor(): ?User
    {
        return $this->instructor;
    }

    public function setInstructor(?User $instructor): static
    {
        $this->instructor = $instructor;

        return $this;
    }
}

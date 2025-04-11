<?php

namespace App\Entity;

use ApiPlatform\Metadata\ApiResource;
use ApiPlatform\Metadata\Get;
use ApiPlatform\Metadata\GetCollection;
use ApiPlatform\Metadata\Patch;
use ApiPlatform\Metadata\Post;
use App\Repository\CarRepository;
use DateTime;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\HasLifecycleCallbacks]
#[ORM\Table(name: 'car')]
#[ORM\Entity(repositoryClass: CarRepository::class)]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Post(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_INSTRUCTOR')"),
        new Patch(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_INSTRUCTOR')"),
    ],
    normalizationContext: ['groups' => ['cars:read']],
    paginationEnabled: false,
)]
class Car
{
    public function __toString(): string
    {
        return $this->carMark ." ". $this->carModel ?? 'Без названия';
    }

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups(['cars:read', 'instructors:read'])]
    private ?int $id = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['cars:read', 'instructors:read'])]
    private ?string $carMark = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['cars:read', 'instructors:read'])]
    private ?string $carModel = null;

    #[ORM\Column(length: 10)]
    #[Groups(['cars:read', 'instructors:read'])]
    private ?string $stateNumber = null;

    #[ORM\Column(nullable: true)]
    #[Groups(['cars:read', 'instructors:read'])]
    private ?DateTime $productionYear = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['cars:read', 'instructors:read'])]
    private ?string $vinNumber = null;

    #[ORM\Column(nullable: true)]
    #[Groups(['cars:read'])]
    private ?bool $isFree = null;

    #[ORM\Column(nullable: true)]
    #[Groups(['cars:read'])]
    private ?bool $isActive = null;

    #[ORM\ManyToOne(inversedBy: 'cars')]
    #[ORM\JoinColumn(name: "belongs_to_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    private ?User $belongsTo = null;

    #[ORM\ManyToOne(inversedBy: 'cars')]
    #[ORM\JoinColumn(name: "category_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups(['cars:read', 'instructors:read'])]
    private ?Category $category = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getCarMark(): ?string
    {
        return $this->carMark;
    }

    public function setCarMark(?string $carMark): static
    {
        $this->carMark = $carMark;

        return $this;
    }

    public function getCarModel(): ?string
    {
        return $this->carModel;
    }

    public function setCarModel(?string $carModel): static
    {
        $this->carModel = $carModel;

        return $this;
    }

    public function getStateNumber(): ?string
    {
        return $this->stateNumber;
    }

    public function setStateNumber(string $stateNumber): static
    {
        $this->stateNumber = $stateNumber;

        return $this;
    }

    public function getProductionYear(): DateTime
    {
        return $this->productionYear;
    }

    public function setProductionYear(?DateTime $productionYear): static
    {
        $this->productionYear = $productionYear;

        return $this;
    }

    public function getVinNumber(): ?string
    {
        return $this->vinNumber;
    }

    public function setVinNumber(?string $vinNumber): static
    {
        $this->vinNumber = $vinNumber;

        return $this;
    }

    public function isFree(): ?bool
    {
        return $this->isFree;
    }

    public function setIsFree(?bool $isFree): static
    {
        $this->isFree = $isFree;

        return $this;
    }

    public function isActive(): ?bool
    {
        return $this->isActive;
    }

    public function setIsActive(?bool $isActive): static
    {
        $this->isActive = $isActive;

        return $this;
    }

    public function getBelongsTo(): ?User
    {
        return $this->belongsTo;
    }

    public function setBelongsTo(?User $belongsTo): static
    {
        $this->belongsTo = $belongsTo;

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
}

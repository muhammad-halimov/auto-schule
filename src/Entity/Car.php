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
use App\Repository\CarRepository;
use DateTime;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\HttpFoundation\File\File;
use Symfony\Component\Serializer\Annotation\Groups;
use Symfony\Component\Validator\Constraints as Assert;
use Vich\UploaderBundle\Mapping\Annotation as Vich;

#[ORM\HasLifecycleCallbacks]
#[Vich\Uploadable]
#[ORM\Table(name: 'car')]
#[ORM\Entity(repositoryClass: CarRepository::class)]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Post(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_INSTRUCTOR')"),
        new Patch(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_INSTRUCTOR')"),
        new Delete(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_INSTRUCTOR')"),
    ],
    normalizationContext: ['groups' => ['cars:read']],
    paginationEnabled: false,
)]
class Car
{
    use UpdatedAtTrait, CreatedAtTrait;

    public function __construct()
    {
        $this->users = new ArrayCollection();
    }

    public function __toString(): string
    {
        return "$this->carMark $this->carModel" ?? 'Без названия';
    }

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups([
        'cars:read',
        'instructors:read',
        'driveSchedule:read',
        'instructorLessons:read'
    ])]
    private ?int $id = null;

    #[ORM\ManyToOne(inversedBy: 'cars')]
    #[Groups([
        'cars:read',
        'instructors:read',
        'driveSchedule:read',
        'instructorLessons:read'
    ])]
    private ?AutoProducer $carMark = null;

    #[ORM\Column(length: 32, nullable: true)]
    #[Groups([
        'cars:read',
        'instructors:read',
        'driveSchedule:read',
        'instructorLessons:read'
    ])]
    private ?string $carModel = null;

    #[ORM\Column(length: 10)]
    #[Groups(['cars:read', 'instructors:read'])]
    private ?string $stateNumber = null;

    #[ORM\Column(type: 'integer', length: 4, nullable: true)]
    #[Groups(['cars:read', 'instructors:read'])]
    private ?int $productionYear = null;

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
    #[ORM\JoinColumn(name: "category_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups(['cars:read', 'instructors:read'])]
    private ?Category $category = null;

    /**
     * @var Collection<int, User>
     */
    #[ORM\OneToMany(mappedBy: 'car', targetEntity: User::class)]
    private Collection $users;

    #[Vich\UploadableField(mapping: 'auto_photos', fileNameProperty: 'image')]
    #[Assert\Image(mimeTypes: ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'])]
    private ?File $imageFile = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups([
        'cars:read',
        'instructors:read',
        'instructorLessons:read',
        'driveSchedule:read',
    ])]
    private ?string $image = null;

    #[ORM\Column(type: 'integer', nullable: true)]
    #[Groups([
        'cars:read',
        'instructors:read',
        'instructorLessons:read',
        'driveSchedule:read',
    ])]
    private ?int $weight = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups([
        'cars:read',
        'instructors:read',
        'instructorLessons:read',
        'driveSchedule:read',
    ])]
    private ?string $fuelingType = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups([
        'cars:read',
        'instructors:read',
        'instructorLessons:read',
        'driveSchedule:read',
    ])]
    private ?string $fuelType = null;

    #[ORM\Column(type: 'integer', nullable: true)]
    #[Groups([
        'cars:read',
        'instructors:read',
        'instructorLessons:read',
        'driveSchedule:read',
    ])]
    private ?int $places = null;

    #[ORM\Column(type: 'integer', nullable: true)]
    #[Groups([
        'cars:read',
        'instructors:read',
        'instructorLessons:read',
        'driveSchedule:read',
    ])]
    private ?int $horsePower = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups([
        'cars:read',
        'instructors:read',
        'instructorLessons:read',
        'driveSchedule:read',
    ])]
    private ?string $transmission = null;

    public function getId(): ?int
    {
        return $this->id;
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

    public function getProductionYear(): ?string
    {
        return $this->productionYear;
    }

    public function setProductionYear(?string $productionYear): static
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
            $user->setCar($this);
        }

        return $this;
    }

    public function removeUser(User $user): static
    {
        if ($this->users->removeElement($user)) {
            // set the owning side to null (unless already changed)
            if ($user->getCar() === $this) {
                $user->setCar(null);
            }
        }

        return $this;
    }

    public function getCarMark(): ?AutoProducer
    {
        return $this->carMark;
    }

    public function setCarMark(?AutoProducer $carMark): static
    {
        $this->carMark = $carMark;

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

    public function getWeight(): ?int
    {
        return $this->weight;
    }

    public function setWeight(?int $weight): Car
    {
        $this->weight = $weight;
        return $this;
    }

    public function getFuelingType(): ?string
    {
        return $this->fuelingType;
    }

    public function setFuelingType(?string $fuelingType): Car
    {
        $this->fuelingType = $fuelingType;
        return $this;
    }

    public function getFuelType(): ?string
    {
        return $this->fuelType;
    }

    public function setFuelType(?string $fuelType): Car
    {
        $this->fuelType = $fuelType;
        return $this;
    }

    public function getPlaces(): ?int
    {
        return $this->places;
    }

    public function setPlaces(?int $places): Car
    {
        $this->places = $places;
        return $this;
    }

    public function getHorsePower(): ?int
    {
        return $this->horsePower;
    }

    public function setHorsePower(?int $horsePower): Car
    {
        $this->horsePower = $horsePower;
        return $this;
    }

    public function getTransmission(): ?string
    {
        return $this->transmission;
    }

    public function setTransmission(?string $transmission): Car
    {
        $this->transmission = $transmission;
        return $this;
    }
}

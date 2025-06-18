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
use App\Repository\AutoProducerRepository;
use DateTimeInterface;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\HasLifecycleCallbacks]
#[ORM\Table(name: 'auto_producer')]
#[ORM\Entity(repositoryClass: AutoProducerRepository::class)]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Post(),
        new Patch(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_INSTRUCTOR')"),
        new Delete(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_INSTRUCTOR')"),
    ],
    normalizationContext: ['groups' => ['auto_producers:read']],
    paginationEnabled: false,
)]
class AutoProducer
{
    use updatedAtTrait, createdAtTrait;

    public function __construct()
    {
        $this->cars = new ArrayCollection();
    }

    public function __toString(): string
    {
        return "$this->title";
    }

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups([
        'cars:read',
        'instructors:read',
        'driveSchedule:read',
        'instructorLessons:read',
        'auto_producers:read'
    ])]
    private ?int $id = null;

    #[ORM\Column(length: 64, nullable: true)]
    #[Groups([
        'cars:read',
        'instructors:read',
        'driveSchedule:read',
        'instructorLessons:read',
        'auto_producers:read'
    ])]
    private ?string $title = null;

    #[ORM\Column(type: Types::DATE_MUTABLE, nullable: true)]
    #[Groups(['auto_producers:read'])]
    private ?DateTimeInterface $established = null;

    #[ORM\Column(length: 64, nullable: true)]
    #[Groups(['auto_producers:read'])]
    private ?string $headquarters = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    #[Groups(['autodromes:read', 'exams:read', 'auto_producers:read'])]
    private ?string $description = null;

    /**
     * @var Collection<int, Car>
     */
    #[ORM\OneToMany(mappedBy: 'carMark', targetEntity: Car::class)]
    private Collection $cars;

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

    public function getEstablished(): ?DateTimeInterface
    {
        return $this->established;
    }

    public function setEstablished(?DateTimeInterface $established): static
    {
        $this->established = $established;

        return $this;
    }

    public function getHeadquarters(): ?string
    {
        return $this->headquarters;
    }

    public function setHeadquarters(?string $headquarters): static
    {
        $this->headquarters = $headquarters;

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

    /**
     * @return Collection<int, Car>
     */
    public function getCars(): Collection
    {
        return $this->cars;
    }

    public function getCarsCount(): int
    {
        return $this->cars->count();
    }

    public function addCar(Car $car): static
    {
        if (!$this->cars->contains($car)) {
            $this->cars->add($car);
            $car->setCarMark($this);
        }

        return $this;
    }

    public function removeCar(Car $car): static
    {
        if ($this->cars->removeElement($car)) {
            // set the owning side to null (unless already changed)
            if ($car->getCarMark() === $this) {
                $car->setCarMark(null);
            }
        }

        return $this;
    }
}

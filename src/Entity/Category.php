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
use App\Repository\ExamRepository;
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
        new Post(),
        new Patch(),
    ],
    normalizationContext: ['groups' => ['category:read']],
    paginationEnabled: false,
)]
class Category
{
    use UpdatedAtTrait, CreatedAtTrait;

    public function __toString()
    {
        return $this->title ?? 'Без названия';
    }

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups(['category:read', 'exams:read'])]
    private ?int $id = null;

    #[ORM\Column(type: Types::STRING, nullable: true)]
    #[Groups(['category:read', 'exams:read'])]
    private ?string $title = null;

    #[ORM\ManyToOne(inversedBy: 'categories')]
    #[ORM\JoinColumn(name: "category_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    private ?Exam $category = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    #[Groups(['category:read', 'exams:read'])]
    private ?string $description = null;

    /**
     * @var Collection<int, Car>
     */
    #[ORM\OneToMany(mappedBy: 'category', targetEntity: Car::class)]
    private Collection $cars;

    public function __construct()
    {
        $this->cars = new ArrayCollection();
    }

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
}

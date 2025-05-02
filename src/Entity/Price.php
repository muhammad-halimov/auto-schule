<?php

namespace App\Entity;

use ApiPlatform\Metadata\ApiResource;
use ApiPlatform\Metadata\Get;
use ApiPlatform\Metadata\GetCollection;
use ApiPlatform\Metadata\Patch;
use ApiPlatform\Metadata\Post;
use App\Entity\Traits\CreatedAtTrait;
use App\Entity\Traits\UpdatedAtTrait;
use App\Repository\PriceRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Attribute\Groups;

#[ORM\Table(name: 'price')]
#[ORM\HasLifecycleCallbacks]
#[ORM\Entity(repositoryClass: PriceRepository::class)]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Post(security: "is_granted('ROLE_ADMIN')"),
        new Patch(security: "is_granted('ROLE_ADMIN')"),
    ],
    normalizationContext: ['groups' => ['prices:read']],
    paginationEnabled: false,
)]
class Price
{
    use UpdatedAtTrait, CreatedAtTrait;

    public function __construct()
    {
        $this->instructorLessons = new ArrayCollection();
    }

    public function __toString(): string
    {
        return "Цена: $this->price руб; Категория: $this->category;";
    }

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups(['prices:read', 'instructorLessons:read', 'driveSchedule:read'])]
    private ?int $id = null;

    #[ORM\Column(nullable: true)]
    #[Groups(['prices:read', 'instructorLessons:read', 'driveSchedule:read'])]
    private ?int $price = null;

    #[ORM\ManyToOne(inversedBy: 'prices')]
    #[Groups(['prices:read'])]
    private ?Category $category = null;

    /**
     * @var Collection<int, InstructorLesson>
     */
    #[ORM\OneToMany(mappedBy: 'price', targetEntity: InstructorLesson::class)]
    private Collection $instructorLessons;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getPrice(): ?int
    {
        return $this->price;
    }

    public function setPrice(?int $price): static
    {
        $this->price = $price;

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
            $instructorLesson->setPrice($this);
        }

        return $this;
    }

    public function removeInstructorLesson(InstructorLesson $instructorLesson): static
    {
        if ($this->instructorLessons->removeElement($instructorLesson)) {
            // set the owning side to null (unless already changed)
            if ($instructorLesson->getPrice() === $this) {
                $instructorLesson->setPrice(null);
            }
        }

        return $this;
    }
}

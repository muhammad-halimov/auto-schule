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

    public function __construct(){}

    public function __toString(): string
    {
        return "Категория: $this->category; Цена: $this->price руб;";
    }

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups(['prices:read', 'instructorLessons:read', 'driveSchedule:read'])]
    private ?int $id = null;

    #[ORM\Column(nullable: true)]
    #[Groups(['prices:read', 'instructorLessons:read', 'driveSchedule:read'])]
    private ?int $price = null;

    #[ORM\OneToOne(inversedBy: 'price', cascade: ['persist', 'remove'])]
    private ?Category $category = null;

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
}

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
use App\Repository\ReviewRepository;
use DateTime;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\HttpFoundation\File\File;
use Symfony\Component\Serializer\Annotation\Groups;
use Symfony\Component\Validator\Constraints as Assert;
use Vich\UploaderBundle\Mapping\Annotation as Vich;

#[ORM\Entity(repositoryClass: ReviewRepository::class)]
#[ORM\Table(name: 'review')]
#[ORM\HasLifecycleCallbacks]
#[Vich\Uploadable]
#[ApiResource(
    operations: [
        new Get(),
        new GetCollection(),
        new Delete(security: "
            is_granted('ROLE_ADMIN') or 
            is_granted('ROLE_STUDENT')
        "),
    ],
    normalizationContext: ['groups' => ['reviews:read']],
    paginationEnabled: false,
)]
class Review
{
    use UpdatedAtTrait, CreatedAtTrait;

    public function __toString()
    {
        return $this->title ?? 'Без названия';
    }

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups(['reviews:read', 'students:read'])]
    private ?int $id = null;

    #[ORM\Column(length: 64, nullable: true)]
    #[Groups(['reviews:read', 'students:read'])]
    private ?string $title = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    #[Groups(['reviews:read', 'students:read'])]
    private ?string $description = null;

    #[ORM\ManyToOne(inversedBy: 'reviews')]
    #[ORM\JoinColumn(name: "publisher_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups(['reviews:read'])]
    private ?User $publisher = null;

    #[Vich\UploadableField(mapping: 'review_images', fileNameProperty: 'image')]
    #[Assert\Image(mimeTypes: ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'])]
    private ?File $imageFile = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['reviews:read'])]
    private ?string $image = null;

    #[ORM\ManyToOne(inversedBy: 'reviews')]
    #[ORM\JoinColumn(name: "course_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups(['reviews:read'])]
    private ?Course $course = null;

    #[ORM\ManyToOne(inversedBy: 'reviewRepresentativePerson')]
    #[ORM\JoinColumn(name: "representative_figure_id", referencedColumnName: "id", nullable: true, onDelete: "SET NULL")]
    #[Groups(['reviews:read'])]
    private ?User $representativeFigure = null;

    #[ORM\Column(type: 'string', length: 15, nullable: true)]
    #[Groups(['reviews:read'])]
    private ?string $type = null;

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

    public function getPublisher(): ?User
    {
        return $this->publisher;
    }

    public function setPublisher(?User $publisher): static
    {
        $this->publisher = $publisher;

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

    public function getCourse(): ?Course
    {
        return $this->course;
    }

    public function setCourse(?Course $course): static
    {
        $this->course = $course;

        return $this;
    }

    public function getRepresentativeFigure(): ?User
    {
        return $this->representativeFigure;
    }

    public function setRepresentativeFigure(?User $representativeFigure): static
    {
        $this->representativeFigure = $representativeFigure;

        return $this;
    }

    public function getType(): ?string
    {
        return $this->type;
    }

    public function setType(?string $type): Review
    {
        $this->type = $type;
        return $this;
    }
}

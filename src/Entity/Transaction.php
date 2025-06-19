<?php

namespace App\Entity;

use ApiPlatform\Metadata\ApiResource;
use ApiPlatform\Metadata\Delete;
use ApiPlatform\Metadata\Get;
use ApiPlatform\Metadata\GetCollection;
use ApiPlatform\Metadata\Patch;
use ApiPlatform\Metadata\Post;
use App\Controller\Api\Filter\Transaction\SingleTransactionUserFilterController;
use App\Controller\Api\Filter\Transaction\TransactionUserFilterController;
use App\Entity\Traits\CreatedAtTrait;
use App\Entity\Traits\UpdatedAtTrait;
use App\Repository\TransactionRepository;
use DateTime;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Groups;

#[ORM\Entity(repositoryClass: TransactionRepository::class)]
#[ORM\Table(name: 'transaction')]
#[ORM\HasLifecycleCallbacks]
#[ApiResource(
    operations: [
        new Get(security: "is_granted('ROLE_ADMIN')"),
        new Get(
            uriTemplate: '/transaction_of_student/{id}',
            controller: SingleTransactionUserFilterController::class,
            security: "
                is_granted('ROLE_ADMIN') or 
                is_granted('ROLE_STUDENT')
        "),
        new GetCollection(security: "is_granted('ROLE_ADMIN')"),
        new GetCollection(
            uriTemplate: '/transactions_filtered/{id}',
            controller: TransactionUserFilterController::class,
            security: "
                is_granted('ROLE_ADMIN') or
                is_granted('ROLE_STUDENT')
        "),
        new Post(security: "is_granted('ROLE_ADMIN') or is_granted('ROLE_STUDENT')"),
        new Patch(security: "is_granted('ROLE_ADMIN')"),
        new Delete(security: "is_granted('ROLE_ADMIN')")
    ],
    normalizationContext: ['groups' => ['transactions:read']],
    paginationEnabled: false,
)]
class Transaction
{
    use UpdatedAtTrait, CreatedAtTrait;

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups([
        'transactions:read'
    ])]
    private ?int $id = null;

    #[ORM\ManyToOne(inversedBy: 'transactions')]
    #[Groups([
        'transactions:read'
    ])]
    private ?User $user = null;

    #[ORM\ManyToOne(inversedBy: 'transactions')]
    #[Groups([
        'transactions:read'
    ])]
    private ?Course $course = null;

    #[ORM\Column(type: Types::DATETIME_MUTABLE, nullable: true)]
    #[Groups([
        'transactions:read'
    ])]
    private ?DateTime $transactionDatetime = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getUser(): ?User
    {
        return $this->user;
    }

    public function setUser(?User $user): static
    {
        $this->user = $user;

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

    public function getTransactionDatetime(): ?DateTime
    {
        return $this->transactionDatetime;
    }

    #[ORM\PrePersist]
    public function setTransactionDatetime(): void
    {
        $this->transactionDatetime = new DateTime();
    }
}

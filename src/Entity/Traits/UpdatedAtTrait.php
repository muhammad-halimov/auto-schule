<?php

namespace App\Entity\Traits;

use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Serializer\Annotation\Ignore;

#[Orm\HasLifecycleCallbacks]
trait UpdatedAtTrait
{
    /**
     * @var \DateTime
     */
    #[ORM\Column(type: 'datetime', nullable: false)]
    #[Ignore]
    protected $updatedAt;

    public function getUpdatedAt(): \DateTime
    {
        return $this->updatedAt;
    }

    #[ORM\PreUpdate]
    #[ORM\PrePersist]
    public function setUpdatedAt($updatedAt): void
    {
        $this->updatedAt = new \DateTime();
    }
}

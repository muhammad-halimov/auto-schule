<?php

namespace App\Entity;

use App\Entity\Traits\CreatedAtTrait;
use App\Entity\Traits\UpdatedAtTrait;
use App\Repository\TeacherLessonVideoRepository;
use DateTime;
use Doctrine\ORM\Mapping as ORM;

use Symfony\Component\HttpFoundation\File\File;
use Symfony\Component\Serializer\Annotation\Groups;
use Symfony\Component\Validator\Constraints as Assert;
use Vich\UploaderBundle\Mapping\Annotation as Vich;

#[ORM\HasLifecycleCallbacks]
#[Vich\Uploadable]
#[ORM\Entity(repositoryClass: TeacherLessonVideoRepository::class)]
class TeacherLessonVideo
{
    use CreatedAtTrait, UpdatedAtTrait;

    public function __toString()
    {
        return $this->video ?? 'Без названия';
    }

    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    #[Groups(['teacherLessons:read', 'students:read'])]
    private ?int $id = null;

    #[Vich\UploadableField(mapping: 'lessons_videos', fileNameProperty: 'video')]
    #[Assert\File(mimeTypes: ['video/mp4', 'video/webm', 'video/avi'])]
    private ?File $videoFile = null;

    #[ORM\Column(length: 255, nullable: true)]
    #[Groups(['teacherLessons:read', 'students:read'])]
    private ?string $video = null;

    #[ORM\ManyToOne(inversedBy: 'videos')]
    private ?TeacherLesson $teacherLesson = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getVideo(): ?string
    {
        return $this->video;
    }

    public function setVideo(?string $video): static
    {
        $this->video = $video;

        return $this;
    }

    public function getVideoFile(): ?File
    {
        return $this->videoFile;
    }

    public function setVideoFile(?File $videoFile): self
    {
        $this->videoFile = $videoFile;

        if (null !== $videoFile) {
            $this->updatedAt = new DateTime();
        }

        return $this;
    }

    public function getTeacherLesson(): ?TeacherLesson
    {
        return $this->teacherLesson;
    }

    public function setTeacherLesson(?TeacherLesson $teacherLesson): static
    {
        $this->teacherLesson = $teacherLesson;

        return $this;
    }
}

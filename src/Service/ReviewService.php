<?php

namespace App\Service;

use App\Entity\Review;
use App\Repository\CourseRepository;
use App\Repository\ReviewRepository;
use App\Repository\UserRepository;
use Doctrine\ORM\EntityManagerInterface;
use Exception;
use InvalidArgumentException;
use Symfony\Component\HttpFoundation\Request;
use Vich\UploaderBundle\Handler\UploadHandler;

readonly class ReviewService
{
    public function __construct(
        private EntityManagerInterface $em,
        private UploadHandler $uploadHandler,
        private UserRepository $userRepository,
        private CourseRepository $courseRepository,
        private ReviewRepository $reviewRepository,
    ) {}

    public function postReview(Request $request): void
    {
        try {
            $review = new Review();
            $data = $request->request->all();
            $files = $request->files->all();

            if (!$data['publisher'] || !$data['course']) {
                throw new InvalidArgumentException("Обязательный аттрибут пропущен.");
            }

            $review->setTitle($data['title']);
            $review->setDescription($data['description']);
            $review->setPublisher($this->userRepository->find($data['publisher']));
            $review->setCourse($this->courseRepository->find($data['course']));

            // Handle file upload with VichUploader
            if (isset($files['review_image'])) {
                $review->setImageFile($files['review_image']);
                $this->uploadHandler->upload($review, 'imageFile');
            }

            $this->em->persist($review);
            $this->em->flush();
        } catch (Exception $exception) {
            throw new InvalidArgumentException("Произошла ошибка: {$exception->getMessage()}");
        }
    }

    public function patchReview(Request $request): void
    {
        try {
            $data = $request->request->all();
            $files = $request->files->all();
            $review = $this->reviewRepository->find($data['id']);

            if (!$review || !$data['publisher'] || !$data['course']) {
                throw new InvalidArgumentException("
                    Отзыв с ID {$data['id']} не найден. 
                    Либо обязательный аттрибут пропущен
                ");
            }

            $review->setTitle($data['title']);
            $review->setDescription($data['description']);
            $review->setPublisher($this->userRepository->find($data['publisher']));
            $review->setCourse($this->courseRepository->find($data['course']));

            // Handle file upload with VichUploader
            if (isset($files['review_image'])) {
                $review->setImageFile($files['review_image']);
                $this->uploadHandler->upload($review, 'imageFile');
            }

            $this->em->flush();
        } catch (Exception $exception) {
            throw new InvalidArgumentException("Произошла ошибка: {$exception->getMessage()}");
        }
    }
}
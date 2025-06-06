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
            $data = $request->request->all();
            $files = $request->files->all();

            // Проверка обязательных полей
            if (empty($data['publisher']) || empty($data['type']) || (empty($data['course']) && empty($data['representativeFigure']))) {
                throw new InvalidArgumentException("Пропущены обязательные атрибуты: publisher, type, course/representativeFigure.");
            }

            $review = new Review();

            // Установка связей
            if (!empty($data['course'])) {
                $course = $this->courseRepository->find($data['course']);
                if (!$course) {
                    throw new InvalidArgumentException("Курс с ID {$data['course']} не найден.");
                }
                $review->setCourse($course);
            } elseif (!empty($data['representativeFigure'])) {
                $representative = $this->userRepository->find($data['representativeFigure']);
                if (!$representative) {
                    throw new InvalidArgumentException("Пользователь (representativeFigure) с ID {$data['representativeFigure']} не найден.");
                }
                $review->setRepresentativeFigure($representative);
            }

            $publisher = $this->userRepository->find($data['publisher']);
            if (!$publisher) {
                throw new InvalidArgumentException("Пользователь (publisher) с ID {$data['publisher']} не найден.");
            }

            $review
                ->setTitle($data['title'] ?? '')
                ->setDescription($data['description'] ?? '')
                ->setPublisher($publisher)
                ->setType($data['type']);

            // Обработка файла
            if (!empty($files['review_image'])) {
                $review->setImageFile($files['review_image']);
                $this->uploadHandler->upload($review, 'imageFile');
            }

            $this->em->persist($review);
            $this->em->flush();
        } catch (Exception $exception) {
            throw new InvalidArgumentException($exception->getMessage());
        }
    }

    public function patchReview(Request $request): void
    {
        try {
            $data = $request->request->all();
            $files = $request->files->all();

            if (empty($data['id'])) {
                throw new InvalidArgumentException("Не передан ID отзыва.");
            }

            $review = $this->reviewRepository->find($data['id']);
            if (!$review) {
                throw new InvalidArgumentException("Отзыв с ID {$data['id']} не найден.");
            }

            if (empty($data['publisher']) || empty($data['type']) || (empty($data['course']) && empty($data['representativeFigure']))) {
                throw new InvalidArgumentException("Пропущены обязательные атрибуты: publisher, type, course/representativeFigure.");
            }

            // Установка связей
            if (!empty($data['course'])) {
                $course = $this->courseRepository->find($data['course']);
                if (!$course) {
                    throw new InvalidArgumentException("Курс с ID {$data['course']} не найден.");
                }
                $review->setCourse($course);
                $review->setRepresentativeFigure(null); // Обнуляем, если переключили
            } elseif (!empty($data['representativeFigure'])) {
                $representative = $this->userRepository->find($data['representativeFigure']);
                if (!$representative) {
                    throw new InvalidArgumentException("Пользователь (representativeFigure) с ID {$data['representativeFigure']} не найден.");
                }
                $review->setRepresentativeFigure($representative);
                $review->setCourse(null); // Обнуляем, если переключили
            }

            $publisher = $this->userRepository->find($data['publisher']);
            if (!$publisher) {
                throw new InvalidArgumentException("Пользователь (publisher) с ID {$data['publisher']} не найден.");
            }

            $review
                ->setTitle($data['title'] ?? '')
                ->setDescription($data['description'] ?? '')
                ->setPublisher($publisher)
                ->setType($data['type']);

            if (!empty($files['review_image'])) {
                $review->setImageFile($files['review_image']);
                $this->uploadHandler->upload($review, 'imageFile');
            }

            $this->em->flush();
        } catch (Exception $exception) {
            throw new InvalidArgumentException($exception->getMessage());
        }
    }
}
<?php

namespace App\DataFixture;

use App\Entity\Review;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class ReviewFixture extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $review1 = new Review();
        $review2 = new Review();

        $reviewsArr = [
            $review1,
            $review2,
        ];

        $review1->setTitle('Классный курс!');
        $review1->setDescription('Мне очень понравилось. Я доволен');
        $review1->setCourse($this->getReference('courseCategoryB'));

        $review2->setTitle('Лучше не бывает!');
        $review2->setDescription('Очень крутой курс, теперь я крутой водитель');
        $review2->setCourse($this->getReference('courseCategoryA'));

        foreach ($reviewsArr as $review) {
            $manager->persist($review);
        }

        $this->addReference('review1', $review1);
        $this->addReference('review2', $review2);

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [
            CourseFixture::class,
        ];
    }
}
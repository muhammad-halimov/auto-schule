<?php

namespace App\DataFixture;

use App\Entity\Course;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class CourseFixture extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $courseCategoryB = new Course();
        $courseCategoryA = new Course();
        $coursesArr = [$courseCategoryA, $courseCategoryB];

        $courseCategoryB->setTitle('Категория B. Модерн');
        $courseCategoryB->setCategory($this->getReference('category_b_alt'));
        $courseCategoryB->setDescription('Полный курс подготовки водителей категории B: теория, практика, городское вождение.');

        $courseCategoryA->setTitle('Категория A. Мото');
        $courseCategoryA->setCategory($this->getReference('category_a_alt'));
        $courseCategoryA->setDescription('Курс для водителей мотоциклов категории A: основное управление, маневрирование и безопасность.');

        foreach ($coursesArr as $course) {
            $manager->persist($course);
        }

        $this->addReference('courseCategoryA', $courseCategoryA);
        $this->addReference('courseCategoryB', $courseCategoryB);

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [
            CategoryFixture::class,
        ];
    }
}
<?php

namespace App\DataFixture\TeacherLessonFixture;

use App\DataFixture\CourseFixture;
use App\DataFixture\TeacherFixture;
use App\Entity\TeacherLesson;
use DateTime;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class CategoryALessonFixture extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $categoryALesson1 = new TeacherLesson();
        $categoryALesson2 = new TeacherLesson();
        $categoryALesson3 = new TeacherLesson();
        $categoryALessonArr = [$categoryALesson3, $categoryALesson2, $categoryALesson1];

        $categoryALesson1->setTitle('Основы управления мотоциклом');
        $categoryALesson1->setTeacher($this->getReference('teacher1'));
        $categoryALesson1->setType('offline');
        $categoryALesson1->setOrderNumber(3);
        $categoryALesson1->setDate(new DateTime('2025-05-15T10:00:00'));
        $categoryALesson1->setDescription('Правила посадки, положения тела, техника балансировки.');
        $categoryALesson1->setCourse($this->getReference('courseCategoryA'));

        $categoryALesson2->setTitle('Фигурное вождение');
        $categoryALesson2->setTeacher($this->getReference('teacher2'));
        $categoryALesson2->setType('online');
        $categoryALesson2->setOrderNumber(2);
        $categoryALesson2->setDate(new DateTime('2025-05-15T10:00:00'));
        $categoryALesson2->setDescription('Техника поворотов на малой скорости.');
        $categoryALesson2->setCourse($this->getReference('courseCategoryA'));

        $categoryALesson3->setTitle('Экстренное торможение и объезд препятствий');
        $categoryALesson3->setTeacher($this->getReference('teacher1'));
        $categoryALesson3->setType('online');
        $categoryALesson3->setOrderNumber(1);
        $categoryALesson3->setDate(new DateTime('2025-05-15T10:00:00'));
        $categoryALesson3->setDescription('Торможение с разных скоростей, объезд внезапного препятствия.');
        $categoryALesson3->setCourse($this->getReference('courseCategoryA'));

        foreach ($categoryALessonArr as $category) {
            $manager->persist($category);
        }

        $this->addReference('categoryALesson1', $categoryALesson1);
        $this->addReference('categoryALesson2', $categoryALesson2);
        $this->addReference('categoryALesson3', $categoryALesson3);

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [
            TeacherFixture::class,
            CourseFixture::class,
        ];
    }
}
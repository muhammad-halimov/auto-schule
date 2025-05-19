<?php

namespace App\DataFixture\TeacherLessonFixture;

use App\DataFixture\CourseFixture;
use App\DataFixture\TeacherFixture;
use App\Entity\TeacherLesson;
use DateTime;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class CategoryBLessonFixture extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $categoryBLesson1 = new TeacherLesson();
        $categoryBLesson2 = new TeacherLesson();
        $categoryBLesson3 = new TeacherLesson();
        $categoryBLessonArr = [$categoryBLesson3, $categoryBLesson2, $categoryBLesson1];

        $categoryBLesson1->setTitle('Начало движения и основы ПДД');
        $categoryBLesson1->setTeacher($this->getReference('teacher1'));
        $categoryBLesson1->setType('offline');
        $categoryBLesson1->setOrderNumber(3);
        $categoryBLesson1->setDate(new DateTime('2025-05-15T10:00:00'));
        $categoryBLesson1->setDescription('Сигналы, зеркала, мёртвые зоны, приоритеты.');
        $categoryBLesson1->setCourse($this->getReference('courseCategoryB'));

        $categoryBLesson2->setTitle('Маневрирование и парковка');
        $categoryBLesson2->setTeacher($this->getReference('teacher2'));
        $categoryBLesson2->setType('online');
        $categoryBLesson2->setOrderNumber(2);
        $categoryBLesson2->setDate(new DateTime('2025-05-15T10:00:00'));
        $categoryBLesson2->setDescription('Правила остановки и стоянки.');
        $categoryBLesson2->setCourse($this->getReference('courseCategoryB'));

        $categoryBLesson3->setTitle('Городское движение');
        $categoryBLesson3->setTeacher($this->getReference('teacher1'));
        $categoryBLesson3->setType('online');
        $categoryBLesson3->setOrderNumber(1);
        $categoryBLesson3->setDate(new DateTime('2025-05-15T10:00:00'));
        $categoryBLesson3->setDescription('Движение в потоке, проезд перекрёстков, соблюдение дистанции.');
        $categoryBLesson3->setCourse($this->getReference('courseCategoryB'));

        foreach ($categoryBLessonArr as $category) {
            $manager->persist($category);
        }

        $this->addReference('categoryBLesson1', $categoryBLesson1);
        $this->addReference('categoryBLesson2', $categoryBLesson2);
        $this->addReference('categoryBLesson3', $categoryBLesson3);

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
<?php

namespace App\DataFixture;

use App\Entity\InstructorLesson;
use DateTime;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class InstructorLessonFixture extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $instructorLesson1 = new InstructorLesson();
        $instructorLesson2 = new InstructorLesson();
        $instructorLessons = [$instructorLesson1, $instructorLesson2];

        $instructorLesson1->setInstructor($this->getReference('instructor1'));
        $instructorLesson1->setAutodrome($this->getReference('autodrome_kirova'));
        $instructorLesson1->setCategory($this->getReference('category_b'));
        // $instructorLesson1->setStudent($this->getReference('student1'));
        $instructorLesson1->setDate(new DateTime('2025-05-15T10:00:00'));

        $instructorLesson2->setInstructor($this->getReference('instructor2'));
        $instructorLesson2->setAutodrome($this->getReference('autodrome_pulkovo'));
        $instructorLesson2->setCategory($this->getReference('category_b'));
        // $instructorLesson2->setStudent($this->getReference('student2'));
        $instructorLesson2->setDate(new DateTime('2025-05-15T11:30:00'));

        foreach ($instructorLessons as $instructorLesson) {
            $manager->persist($instructorLesson);
        }

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [
            CategoryFixture::class,
            AutodromeFixture::class,
            InstructorFixture::class,
            StudentFixture::class,
        ];
    }
}
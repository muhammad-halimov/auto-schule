<?php

namespace App\DataFixture\CourseQuizAnswerFixture;

use App\Entity\CourseQuizAnswers;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class CourseQuizAnswerFixture4 extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $courseQuiz4Answer1 = new CourseQuizAnswers();
        $courseQuiz4Answer2 = new CourseQuizAnswers();
        $courseQuiz4Answer3 = new CourseQuizAnswers();
        $courseQuiz4Answer4 = new CourseQuizAnswers();

        $courseQuizzesAnswers = [
            $courseQuiz4Answer1,
            $courseQuiz4Answer2,
            $courseQuiz4Answer3,
            $courseQuiz4Answer4,
        ];

        $courseQuiz4Answer1->setAnswerText('Разрешено в любом случае.');
        $courseQuiz4Answer1->setStatus(false);

        $courseQuiz4Answer2->setAnswerText('Запрещено.');
        $courseQuiz4Answer2->setStatus(true);

        $courseQuiz4Answer3->setAnswerText('Разрешено при отсутствии других участников движения.');
        $courseQuiz4Answer3->setStatus(false);

        $courseQuiz4Answer4->setAnswerText('Разрешено только в ночное время.');
        $courseQuiz4Answer4->setStatus(false);

        foreach ($courseQuizzesAnswers as $courseQuizzesAnswer) {
            $manager->persist($courseQuizzesAnswer);
        }

        $manager->flush();

        $this->addReference('courseQuiz4Answer1', $courseQuiz4Answer1);
        $this->addReference('courseQuiz4Answer2', $courseQuiz4Answer2);
        $this->addReference('courseQuiz4Answer3', $courseQuiz4Answer3);
        $this->addReference('courseQuiz4Answer4', $courseQuiz4Answer4);
    }

    public function getDependencies(): array
    {
        return [];
    }
}
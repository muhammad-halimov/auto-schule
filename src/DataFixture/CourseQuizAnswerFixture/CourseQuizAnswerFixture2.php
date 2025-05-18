<?php

namespace App\DataFixture\CourseQuizAnswerFixture;

use App\Entity\CourseQuizAnswers;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class CourseQuizAnswerFixture2 extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $courseQuiz2Answer1 = new CourseQuizAnswers();
        $courseQuiz2Answer2 = new CourseQuizAnswers();
        $courseQuiz2Answer3 = new CourseQuizAnswers();
        $courseQuiz2Answer4 = new CourseQuizAnswers();

        $courseQuizzesAnswers = [
            $courseQuiz2Answer1,
            $courseQuiz2Answer2,
            $courseQuiz2Answer3,
            $courseQuiz2Answer4,
        ];

        $courseQuiz2Answer1->setAnswerText('Движение запрещено.');
        $courseQuiz2Answer1->setStatus(false);

        $courseQuiz2Answer2->setAnswerText('Движение разрешено только пешеходам.');
        $courseQuiz2Answer2->setStatus(false);

        $courseQuiz2Answer3->setAnswerText('Неисправность светофора, нужно проезжать перекрёсток, руководствуясь знаками приоритета.');
        $courseQuiz2Answer3->setStatus(true);

        $courseQuiz2Answer4->setAnswerText('Приоритет у общественного транспорта.');
        $courseQuiz2Answer4->setStatus(false);

        foreach ($courseQuizzesAnswers as $courseQuizzesAnswer) {
            $manager->persist($courseQuizzesAnswer);
        }

        $this->addReference('courseQuiz2Answer1', $courseQuiz2Answer1);
        $this->addReference('courseQuiz2Answer2', $courseQuiz2Answer2);
        $this->addReference('courseQuiz2Answer3', $courseQuiz2Answer3);
        $this->addReference('courseQuiz2Answer4', $courseQuiz2Answer4);

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [];
    }
}
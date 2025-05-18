<?php

namespace App\DataFixture\CourseQuizAnswerFixture;

use App\Entity\CourseQuizAnswers;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class CourseQuizAnswerFixture6 extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $courseQuiz6Answer1 = new CourseQuizAnswers();
        $courseQuiz6Answer2 = new CourseQuizAnswers();
        $courseQuiz6Answer3 = new CourseQuizAnswers();
        $courseQuiz6Answer4 = new CourseQuizAnswers();

        $courseQuizzesAnswers = [
            $courseQuiz6Answer1,
            $courseQuiz6Answer2,
            $courseQuiz6Answer3,
            $courseQuiz6Answer4,
        ];

        $courseQuiz6Answer1->setAnswerText('Не менее 3 метров.');
        $courseQuiz6Answer1->setStatus(false);

        $courseQuiz6Answer2->setAnswerText('Не менее 5 метров.');
        $courseQuiz6Answer2->setStatus(true);

        $courseQuiz6Answer3->setAnswerText('Не менее 10 метров.');
        $courseQuiz6Answer3->setStatus(false);

        $courseQuiz6Answer4->setAnswerText('Остановка на переходе разрешена, если нет пешеходов.');
        $courseQuiz6Answer4->setStatus(false);

        foreach ($courseQuizzesAnswers as $courseQuizzesAnswer) {
            $manager->persist($courseQuizzesAnswer);
        }

        $this->addReference('courseQuiz6Answer1', $courseQuiz6Answer1);
        $this->addReference('courseQuiz6Answer2', $courseQuiz6Answer2);
        $this->addReference('courseQuiz6Answer3', $courseQuiz6Answer3);
        $this->addReference('courseQuiz6Answer4', $courseQuiz6Answer4);

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [];
    }
}
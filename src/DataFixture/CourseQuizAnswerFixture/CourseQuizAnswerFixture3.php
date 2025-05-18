<?php

namespace App\DataFixture\CourseQuizAnswerFixture;

use App\Entity\CourseQuizAnswers;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class CourseQuizAnswerFixture3 extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $courseQuiz3Answer1 = new CourseQuizAnswers();
        $courseQuiz3Answer2 = new CourseQuizAnswers();
        $courseQuiz3Answer3 = new CourseQuizAnswers();
        $courseQuiz3Answer4 = new CourseQuizAnswers();

        $courseQuizzesAnswers = [
            $courseQuiz3Answer1,
            $courseQuiz3Answer2,
            $courseQuiz3Answer3,
            $courseQuiz3Answer4,
        ];

        $courseQuiz3Answer1->setAnswerText('50 км/ч');
        $courseQuiz3Answer1->setStatus(true);

        $courseQuiz3Answer2->setAnswerText('60 км/ч');
        $courseQuiz3Answer2->setStatus(false);

        $courseQuiz3Answer3->setAnswerText('40 км/ч');
        $courseQuiz3Answer3->setStatus(false);

        $courseQuiz3Answer4->setAnswerText('30 км/ч');
        $courseQuiz3Answer4->setStatus(false);

        foreach ($courseQuizzesAnswers as $courseQuizzesAnswer) {
            $manager->persist($courseQuizzesAnswer);
        }

        $manager->flush();

        $this->addReference('courseQuiz3Answer1', $courseQuiz3Answer1);
        $this->addReference('courseQuiz3Answer2', $courseQuiz3Answer2);
        $this->addReference('courseQuiz3Answer3', $courseQuiz3Answer3);
        $this->addReference('courseQuiz3Answer4', $courseQuiz3Answer4);
    }

    public function getDependencies(): array
    {
        return [];
    }
}
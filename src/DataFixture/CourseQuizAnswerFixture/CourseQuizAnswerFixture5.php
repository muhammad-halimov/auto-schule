<?php

namespace App\DataFixture\CourseQuizAnswerFixture;

use App\Entity\CourseQuizAnswers;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class CourseQuizAnswerFixture5 extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $courseQuiz5Answer1 = new CourseQuizAnswers();
        $courseQuiz5Answer2 = new CourseQuizAnswers();
        $courseQuiz5Answer3 = new CourseQuizAnswers();
        $courseQuiz5Answer4 = new CourseQuizAnswers();

        $courseQuizzesAnswers = [
            $courseQuiz5Answer1,
            $courseQuiz5Answer2,
            $courseQuiz5Answer3,
            $courseQuiz5Answer4,
        ];

        $courseQuiz5Answer1->setAnswerText('Только габаритные огни.');
        $courseQuiz5Answer1->setStatus(false);

        $courseQuiz5Answer2->setAnswerText('Ближний или противотуманный свет.');
        $courseQuiz5Answer2->setStatus(true);

        $courseQuiz5Answer3->setAnswerText('Только дневные ходовые огни.');
        $courseQuiz5Answer3->setStatus(false);

        $courseQuiz5Answer4->setAnswerText('Свет включать не обязательно.');
        $courseQuiz5Answer4->setStatus(false);

        foreach ($courseQuizzesAnswers as $courseQuizzesAnswer) {
            $manager->persist($courseQuizzesAnswer);
        }

        $this->addReference('courseQuiz5Answer1', $courseQuiz5Answer1);
        $this->addReference('courseQuiz5Answer2', $courseQuiz5Answer2);
        $this->addReference('courseQuiz5Answer3', $courseQuiz5Answer3);
        $this->addReference('courseQuiz5Answer4', $courseQuiz5Answer4);

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [];
    }
}
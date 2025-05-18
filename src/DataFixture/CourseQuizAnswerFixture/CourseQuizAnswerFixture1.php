<?php

namespace App\DataFixture\CourseQuizAnswerFixture;

use App\Entity\CourseQuizAnswers;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class CourseQuizAnswerFixture1 extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $courseQuiz1Answer1 = new CourseQuizAnswers();
        $courseQuiz1Answer2 = new CourseQuizAnswers();
        $courseQuiz1Answer3 = new CourseQuizAnswers();
        $courseQuiz1Answer4 = new CourseQuizAnswers();

        $courseQuizzesAnswers = [
            $courseQuiz1Answer1,
            $courseQuiz1Answer2,
            $courseQuiz1Answer3,
            $courseQuiz1Answer4,
        ];

        $courseQuiz1Answer1->setAnswerText('Подать звуковой сигнал.');
        $courseQuiz1Answer1->setStatus(false);

        $courseQuiz1Answer2->setAnswerText('Убедиться в безопасности манёвра и включить указатель поворота.');
        $courseQuiz1Answer2->setStatus(true);

        $courseQuiz1Answer3->setAnswerText('Быстро начать движение, чтобы не мешать потоку.');
        $courseQuiz1Answer3->setStatus(false);

        $courseQuiz1Answer4->setAnswerText('Пропустить всех пешеходов и автомобили независимо от положения.');
        $courseQuiz1Answer4->setStatus(false);

        foreach ($courseQuizzesAnswers as $courseQuizzesAnswer) {
            $manager->persist($courseQuizzesAnswer);
        }

        $this->addReference('courseQuiz1Answer1', $courseQuiz1Answer1);
        $this->addReference('courseQuiz1Answer2', $courseQuiz1Answer2);
        $this->addReference('courseQuiz1Answer3', $courseQuiz1Answer3);
        $this->addReference('courseQuiz1Answer4', $courseQuiz1Answer4);

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [];
    }
}
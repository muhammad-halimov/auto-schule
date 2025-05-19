<?php

namespace App\DataFixture;

use App\DataFixture\CourseQuizAnswerFixture\CourseQuizAnswerFixture1;
use App\DataFixture\CourseQuizAnswerFixture\CourseQuizAnswerFixture2;
use App\DataFixture\CourseQuizAnswerFixture\CourseQuizAnswerFixture3;
use App\DataFixture\CourseQuizAnswerFixture\CourseQuizAnswerFixture4;
use App\DataFixture\CourseQuizAnswerFixture\CourseQuizAnswerFixture5;
use App\DataFixture\CourseQuizAnswerFixture\CourseQuizAnswerFixture6;
use App\Entity\CourseQuiz;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class CourseQuizFixture extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $courseQuiz1 = new CourseQuiz();
        $courseQuiz2 = new CourseQuiz();
        $courseQuiz3 = new CourseQuiz();
        $courseQuiz4 = new CourseQuiz();
        $courseQuiz5 = new CourseQuiz();
        $courseQuiz6 = new CourseQuiz();

        $courseQuizzes = [
            $courseQuiz1,
            $courseQuiz2,
            $courseQuiz3,
            $courseQuiz4,
            $courseQuiz5,
            $courseQuiz6
        ];

        $courseQuiz1->setQuestion('Что вы должны сделать перед началом движения с места стоянки у тротуара?');
        $courseQuiz1->setOrderNumber(1);
        $courseQuiz1->addAnswer($this->getReference('courseQuiz1Answer1'));
        $courseQuiz1->addAnswer($this->getReference('courseQuiz1Answer2'));
        $courseQuiz1->addAnswer($this->getReference('courseQuiz1Answer3'));
        $courseQuiz1->addAnswer($this->getReference('courseQuiz1Answer4'));
        $courseQuiz1->setCourse($this->getReference('courseCategoryA'));

        $courseQuiz2->setQuestion('Что означает мигающий жёлтый сигнал светофора?');
        $courseQuiz2->setOrderNumber(2);
        $courseQuiz2->addAnswer($this->getReference('courseQuiz2Answer1'));
        $courseQuiz2->addAnswer($this->getReference('courseQuiz2Answer2'));
        $courseQuiz2->addAnswer($this->getReference('courseQuiz2Answer3'));
        $courseQuiz2->addAnswer($this->getReference('courseQuiz2Answer4'));
        $courseQuiz2->setCourse($this->getReference('courseCategoryA'));

        $courseQuiz3->setQuestion('С какой максимальной скоростью разрешается движение в населённом пункте, если нет иных указаний?');
        $courseQuiz3->setOrderNumber(3);
        $courseQuiz3->addAnswer($this->getReference('courseQuiz3Answer1'));
        $courseQuiz3->addAnswer($this->getReference('courseQuiz3Answer2'));
        $courseQuiz3->addAnswer($this->getReference('courseQuiz3Answer3'));
        $courseQuiz3->addAnswer($this->getReference('courseQuiz3Answer4'));
        $courseQuiz3->setCourse($this->getReference('courseCategoryA'));

        $courseQuiz4->setQuestion('Разрешено ли движение задним ходом на перекрёстках?');
        $courseQuiz4->setOrderNumber(1);
        $courseQuiz4->addAnswer($this->getReference('courseQuiz4Answer1'));
        $courseQuiz4->addAnswer($this->getReference('courseQuiz4Answer2'));
        $courseQuiz4->addAnswer($this->getReference('courseQuiz4Answer3'));
        $courseQuiz4->addAnswer($this->getReference('courseQuiz4Answer4'));
        $courseQuiz4->setCourse($this->getReference('courseCategoryB'));

        $courseQuiz5->setQuestion('Какие внешние световые приборы необходимо включить при движении в условиях недостаточной видимости?');
        $courseQuiz5->setOrderNumber(2);
        $courseQuiz5->addAnswer($this->getReference('courseQuiz5Answer1'));
        $courseQuiz5->addAnswer($this->getReference('courseQuiz5Answer2'));
        $courseQuiz5->addAnswer($this->getReference('courseQuiz5Answer3'));
        $courseQuiz5->addAnswer($this->getReference('courseQuiz5Answer4'));
        $courseQuiz5->setCourse($this->getReference('courseCategoryB'));

        $courseQuiz6->setQuestion('Какое минимальное расстояние до пешеходного перехода разрешается остановка автомобиля?');
        $courseQuiz6->setOrderNumber(3);
        $courseQuiz6->addAnswer($this->getReference('courseQuiz6Answer1'));
        $courseQuiz6->addAnswer($this->getReference('courseQuiz6Answer2'));
        $courseQuiz6->addAnswer($this->getReference('courseQuiz6Answer3'));
        $courseQuiz6->addAnswer($this->getReference('courseQuiz6Answer4'));
        $courseQuiz6->setCourse($this->getReference('courseCategoryB'));

        foreach ($courseQuizzes as $courseQuiz) {
            $manager->persist($courseQuiz);
        }

        $this->addReference('courseQuiz1', $courseQuiz1);
        $this->addReference('courseQuiz2', $courseQuiz2);
        $this->addReference('courseQuiz3', $courseQuiz3);
        $this->addReference('courseQuiz4', $courseQuiz4);
        $this->addReference('courseQuiz5', $courseQuiz5);
        $this->addReference('courseQuiz6', $courseQuiz6);

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [
            CourseFixture::class,
            CourseQuizAnswerFixture1::class,
            CourseQuizAnswerFixture2::class,
            CourseQuizAnswerFixture3::class,
            CourseQuizAnswerFixture4::class,
            CourseQuizAnswerFixture5::class,
            CourseQuizAnswerFixture6::class,
        ];
    }
}
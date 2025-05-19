<?php

namespace App\DataFixture\TeacherLessonVideoFixture;

use App\DataFixture\TeacherLessonFixture\CategoryALessonFixture;
use App\DataFixture\TeacherLessonFixture\CategoryBLessonFixture;
use App\Entity\TeacherLessonVideo;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class TeacherLessonVideoFixture extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $lessonVideo1 = new TeacherLessonVideo();
        $lessonVideo2 = new TeacherLessonVideo();
        $lessonVideo3 = new TeacherLessonVideo();
        $lessonVideo4 = new TeacherLessonVideo();
        $lessonVideo5 = new TeacherLessonVideo();
        $lessonVideo6 = new TeacherLessonVideo();
        $lessonVideo7 = new TeacherLessonVideo();
        $lessonVideo8 = new TeacherLessonVideo();

        $teacherLessonsVideos = [
            $lessonVideo1->setVideo('7565438-hd-1080-1920-25fps-6824a89839697830395740.mp4'),
            $lessonVideo2->setVideo('6548176-hd-1280-720-24fps-68134acf801cf941040945.mp4'),

            $lessonVideo3->setVideo('7565438-hd-1080-1920-25fps-6824a89839697830395740.mp4'),
            $lessonVideo4->setVideo('6548176-hd-1280-720-24fps-68134acf801cf941040945.mp4'),

            $lessonVideo5->setVideo('7565438-hd-1080-1920-25fps-6824a89839697830395740.mp4'),
            $lessonVideo6->setVideo('6548176-hd-1280-720-24fps-68134acf801cf941040945.mp4'),

            $lessonVideo7->setVideo('7565438-hd-1080-1920-25fps-6824a89839697830395740.mp4'),
            $lessonVideo8->setVideo('6548176-hd-1280-720-24fps-68134acf801cf941040945.mp4'),
        ];


        // Курс B Урок 1/2
        $teacherLessonsVideos[0]->setTeacherLesson($this->getReference('categoryBLesson3'));
        $teacherLessonsVideos[1]->setTeacherLesson($this->getReference('categoryBLesson3'));
        $teacherLessonsVideos[2]->setTeacherLesson($this->getReference('categoryBLesson2'));
        $teacherLessonsVideos[3]->setTeacherLesson($this->getReference('categoryBLesson2'));

        // Курс A Урок 1/2
        $teacherLessonsVideos[4]->setTeacherLesson($this->getReference('categoryALesson3'));
        $teacherLessonsVideos[5]->setTeacherLesson($this->getReference('categoryALesson3'));
        $teacherLessonsVideos[6]->setTeacherLesson($this->getReference('categoryALesson2'));
        $teacherLessonsVideos[7]->setTeacherLesson($this->getReference('categoryALesson2'));

        foreach ($teacherLessonsVideos as $teacherLessonVideo) {
            $manager->persist($teacherLessonVideo);
        }

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [
            CategoryALessonFixture::class,
            CategoryBLessonFixture::class,
        ];
    }
}
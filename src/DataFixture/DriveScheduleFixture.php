<?php

namespace App\DataFixture;

use App\Entity\DriveSchedule;
use DateTime;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class DriveScheduleFixture extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $driveSchedule1 = new DriveSchedule();
        $driveSchedule2 = new DriveSchedule();
        $driveScheduArr = [$driveSchedule1, $driveSchedule2];

        $driveSchedule1->setDaysOfWeek('Пн,Ср');
        $driveSchedule1->setAutodrome($this->getReference('autodrome_kirova'));
        $driveSchedule1->setCategory($this->getReference('category_b'));
        $driveSchedule1->setTimeFrom(new DateTime('1970-01-01T09:00:00'));
        $driveSchedule1->setTimeTo(new DateTime('1970-01-01T16:00:00'));

        $driveSchedule2->setDaysOfWeek('Пн,Вт,Ср,Сб');
        $driveSchedule2->setAutodrome($this->getReference('autodrome_pulkovo'));
        $driveSchedule2->setCategory($this->getReference('category_b'));
        $driveSchedule2->setTimeFrom(new DateTime('1970-01-01T10:00:00'));
        $driveSchedule2->setTimeTo(new DateTime('1970-01-01T17:30:00'));

        foreach ($driveScheduArr as $driveSchedule) {
            $manager->persist($driveSchedule);
        }

        $this->addReference('driveSchedule1', $driveSchedule1);
        $this->addReference('driveSchedule2', $driveSchedule2);

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [
            CategoryFixture::class,
            AutodromeFixture::class,
        ];
    }
}
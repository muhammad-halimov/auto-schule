<?php

namespace App\DataFixture;

use App\Entity\User;
use DateTime;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class InstructorFixture extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $instructor1 = new User();
        $instructor2 = new User();
        $userArr = [$instructor1, $instructor2];

        $instructor1->setRoles(["ROLE_INSTRUCTOR"]);
        $instructor1->setEmail('xander.fomay@auto-schule.com');
        $instructor1->setName('Александр');
        $instructor1->setSurname('Фомай');
        $instructor1->setPhone('+79998887733');
        $instructor1->setExperience(10);
        $instructor1->setLicense('ASFFZXXF315');
        $instructor1->setPassword('foobar');
        $instructor1->setDateOfBirth(new DateTime('1990-01-01'));
        $instructor1->setHireDate(new DateTime('2025-05-15'));
        $instructor1->setCategory($this->getReference('category_b'));
        $instructor1->setCar($this->getReference('car_mercedes'));
        $instructor1->setIsActive(true);
        $instructor1->setIsApproved(true);

        $instructor2->setRoles(["ROLE_INSTRUCTOR"]);
        $instructor2->setEmail('maximilyan.fomay@auto-schule.com');
        $instructor2->setName('Максимилиан');
        $instructor2->setSurname('Фомай');
        $instructor2->setPhone('+79998887744');
        $instructor2->setExperience(10);
        $instructor2->setLicense('ASFFZXXF316');
        $instructor2->setPassword('foobar');
        $instructor2->setDateOfBirth(new DateTime('1990-01-01'));
        $instructor2->setHireDate(new DateTime('2025-05-15'));
        $instructor2->setCategory($this->getReference('category_b'));
        $instructor2->setCar($this->getReference('car_lada'));
        $instructor2->setIsActive(true);
        $instructor2->setIsApproved(true);

        foreach ($userArr as $user) {
            $manager->persist($user);
        }

        $this->addReference('instructor1', $instructor1);
        $this->addReference('instructor2', $instructor2);

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [
            CategoryFixture::class,
            CarFixture::class,
        ];
    }
}
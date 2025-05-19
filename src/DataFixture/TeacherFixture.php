<?php

namespace App\DataFixture;

use App\Entity\User;
use DateTime;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class TeacherFixture extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $teacher1 = new User();
        $teacher2 = new User();
        $userArr = [$teacher1, $teacher2];

        $teacher1->setRoles(["ROLE_TEACHER"]);
        $teacher1->setEmail('alexsey.alexeev@auto-schule.com');
        $teacher1->setName('Алексей');
        $teacher1->setSurname('Алексеев');
        $teacher1->setPhone('+79998887755');
        $teacher1->setExperience(10);
        $teacher1->setLicense('ASFFZXXF320');
        $teacher1->setPassword('foobar');
        $teacher1->setDateOfBirth(new DateTime('1990-01-01'));
        $teacher1->setHireDate(new DateTime('2025-05-15'));
        $teacher1->setIsActive(true);
        $teacher1->setIsApproved(true);
        $teacher1->setCategory($this->getReference('category_b'));

        $teacher2->setRoles(["ROLE_TEACHER"]);
        $teacher2->setEmail('mihail.alexeev@auto-schule.com');
        $teacher2->setName('Михаил');
        $teacher2->setSurname('Алексеев');
        $teacher2->setPhone('+79998887766');
        $teacher2->setExperience(10);
        $teacher2->setLicense('ASFFZXXF319');
        $teacher2->setPassword('foobar');
        $teacher2->setDateOfBirth(new DateTime('1990-01-01'));
        $teacher2->setHireDate(new DateTime('2025-05-15'));
        $teacher2->setIsActive(true);
        $teacher2->setIsApproved(true);
        $teacher2->setCategory($this->getReference('category_a'));

        foreach ($userArr as $user) {
            $manager->persist($user);
        }

        $this->addReference('teacher1', $teacher1);
        $this->addReference('teacher2', $teacher2);

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [];
    }
}
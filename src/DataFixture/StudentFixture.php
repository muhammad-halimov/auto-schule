<?php

namespace App\DataFixture;

use App\Entity\User;
use DateTime;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;

class StudentFixture extends Fixture
{
    private UserPasswordHasherInterface $userPasswordHasher;

    public function __construct(UserPasswordHasherInterface $userPasswordHasher)
    {
        $this->userPasswordHasher = $userPasswordHasher;
    }

    public function load(ObjectManager $manager): void
    {
        $student1 = new User();
        $student2 = new User();
        $userArr = [$student1, $student2];

        $student1->setRoles(["ROLE_STUDENT"]);
        $student1->setEmail('muhammadi.halimov@icloud.com');
        $student1->setName('Мухаммед');
        $student1->setSurname('Халимов');
        $student1->setPhone('+79918431185');
        $student1->setContract('ASFFZXXF323');
        $student1->setPassword($this->userPasswordHasher->hashPassword($student1, 'foobar'));
        $student1->setDateOfBirth(new DateTime('2005-05-28'));
        $student1->setEnrollDate(new DateTime('2025-05-15'));
        $student1->setIsActive(true);
        $student1->setIsApproved(true);
        $student1->setBalance(60000);
        $student1->addCourse($this->getReference('courseCategoryB'));
        $student1->addInstructorLessonStudent($this->getReference('instructorLesson1'));
        $student1->addReview($this->getReference('review1'));
        $student1->setCategory($this->getReference('category_b'));

        $student2->setRoles(["ROLE_STUDENT"]);
        $student2->setEmail('IlyaShcherbakov2005@mail.ru');
        $student2->setName('Илья');
        $student2->setSurname('Щербаков');
        $student2->setPhone('+79058742391');
        $student2->setContract('ASFFZXXF324');
        $student2->setPassword($this->userPasswordHasher->hashPassword($student2, '00b51b1f'));
        $student2->setDateOfBirth(new DateTime('2005-08-13'));
        $student2->setEnrollDate(new DateTime('2025-05-15'));
        $student2->setIsActive(true);
        $student2->setIsApproved(true);
        $student2->setBalance(60000);
        $student2->addCourse($this->getReference('courseCategoryA'));
        $student2->addCourse($this->getReference('courseCategoryB'));
        $student2->addInstructorLessonStudent($this->getReference('instructorLesson2'));
        $student2->addReview($this->getReference('review2'));
        $student2->setCategory($this->getReference('category_a'));

        foreach ($userArr as $user) {
            $manager->persist($user);
        }

        $this->addReference('student1', $student1);
        $this->addReference('student2', $student2);

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [
            CourseFixture::class,
            InstructorFixture::class,
        ];
    }
}
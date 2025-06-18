<?php

namespace App\DataFixture;

use App\Entity\Transaction;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class TransactionFixture extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $transaction1 = new Transaction();
        $transaction2 = new Transaction();
        $transaction3 = new Transaction();
        $transactionsArr = [
            $transaction1,
            $transaction2,
            $transaction3
        ];

        $transaction1->setUser($this->getReference('student1'));
        $transaction1->setCourse($this->getReference('courseCategoryB'));

        $transaction2->setUser($this->getReference('student2'));
        $transaction2->setCourse($this->getReference('courseCategoryA'));

        $transaction3->setUser($this->getReference('student2'));
        $transaction3->setCourse($this->getReference('courseCategoryB'));

        foreach ($transactionsArr as $transaction) {
            $manager->persist($transaction);
        }

        $this->addReference('transaction1', $transaction1);
        $this->addReference('transaction2', $transaction2);
        $this->addReference('transaction3', $transaction3);

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [
            CourseFixture::class,
            StudentFixture::class,
        ];
    }
}
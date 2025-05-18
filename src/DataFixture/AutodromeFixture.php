<?php

namespace App\DataFixture;

use App\Entity\Autodrome;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class AutodromeFixture extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $autodromeKirova = new Autodrome();
        $autodromePulkovo = new Autodrome();
        $autodromeDomodedovo = new Autodrome();
        $autodromeArr = [$autodromeKirova, $autodromePulkovo, $autodromeDomodedovo];

        $autodromeKirova->setTitle("Кирова");
        $autodromeKirova->setAddress("Ижевск, ул. Кирова, д. 95");
        $autodromeKirova->setDescription("Ижевский автодром");

        $autodromePulkovo->setTitle("Пулково");
        $autodromePulkovo->setAddress("Петербург, ул. Пулково, д. 95");
        $autodromePulkovo->setDescription("Пулковский автодром");

        $autodromeDomodedovo->setTitle("Домодедово");
        $autodromeDomodedovo->setAddress("Москва, ул. Домодедово, д. 95");
        $autodromeDomodedovo->setDescription("Домодедовский автодром");

        foreach ($autodromeArr as $autodrome) {
            $manager->persist($autodrome);
        }

        $this->addReference('autodrome_kirova', $autodromeKirova);
        $this->addReference('autodrome_pulkovo', $autodromePulkovo);
        $this->addReference('autodrome_domodedovo', $autodromeDomodedovo);

        $manager->flush();
    }
}
<?php

namespace App\DataFixture;

use App\Entity\AutoProducer;
use DateTime;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class AutoProducerFixture extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $ladaAutoProducer = new AutoProducer();
        $mercedesAutoProducer = new AutoProducer();
        $renaultAutoProducer = new AutoProducer();
        $producersArr = [$ladaAutoProducer, $mercedesAutoProducer, $renaultAutoProducer];

        $ladaAutoProducer->setTitle('Lada');
        $ladaAutoProducer->setHeadquarters('Россия');
        $ladaAutoProducer->setDescription('Российский автопром');
        $ladaAutoProducer->setEstablished(new DateTime('1950-01-01'));

        $mercedesAutoProducer->setTitle('Mercedes-Benz');
        $mercedesAutoProducer->setHeadquarters('ФРГ, Германия');
        $mercedesAutoProducer->setDescription('Германский автопром');
        $mercedesAutoProducer->setEstablished(new DateTime('1885-01-01'));

        $renaultAutoProducer->setTitle('Renault');
        $renaultAutoProducer->setHeadquarters('Франция');
        $renaultAutoProducer->setDescription('Французский автопром');
        $renaultAutoProducer->setEstablished(new DateTime('1925-01-01'));

        foreach ($producersArr as $producer) {
            $manager->persist($producer);
        }

        $this->addReference('producer_lada', $ladaAutoProducer);
        $this->addReference('producer_mercedes', $mercedesAutoProducer);
        $this->addReference('producer_renault', $renaultAutoProducer);

        $manager->flush();
    }
}
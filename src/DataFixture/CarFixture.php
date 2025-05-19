<?php

namespace App\DataFixture;

use App\Entity\Car;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class CarFixture extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $lada = new Car();
        $mercedes = new Car();
        $renault = new Car();
        $autosArr = [$lada, $mercedes, $renault];

        $lada->setCarMark($this->getReference('producer_lada'));
        $lada->setCarModel('Granta');
        $lada->setStateNumber('A224BC');
        $lada->setProductionYear('2022');
        $lada->setVinNumber('VINLADA224');
        $lada->setIsFree(true);
        $lada->setIsActive(true);

        $mercedes->setCarMark($this->getReference('producer_mercedes'));
        $mercedes->setCarModel('SLR McLaren');
        $mercedes->setStateNumber('A444BC');
        $mercedes->setProductionYear('2004');
        $mercedes->setVinNumber('VINMERCEDER444');
        $mercedes->setImage('mercedes-benz-slr-mclaren-8615164079-6825b3f16f4a2602736041.jpg');
        $mercedes->setIsFree(true);
        $mercedes->setIsActive(true);

        $renault->setCarMark($this->getReference('producer_renault'));
        $renault->setCarModel('Logan');
        $renault->setStateNumber('A379BC');
        $renault->setProductionYear('2010');
        $renault->setVinNumber('VINRENAULT379');
        $renault->setIsFree(true);
        $renault->setIsActive(true);

        foreach ($autosArr as $auto) {
            $manager->persist($auto);
        }

        $this->addReference('car_lada', $lada);
        $this->addReference('car_renault', $renault);
        $this->addReference('car_mercedes', $mercedes);

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [
            AutoProducerFixture::class,
        ];
    }
}
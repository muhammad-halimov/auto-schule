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
        $lada->setProductionYear(2022);
        $lada->setVinNumber('VINLADA224');
        $lada->setIsFree(true);
        $lada->setIsActive(true);
        $lada->setWeight(2.0);
        $lada->setWeightLift(0.450);
        $lada->setFuelType('Бензин');
        $lada->setFuelingType('ДВС (Двигатель внутреннего сгорания)');
        $lada->setPlaces(4);
        $lada->setHorsePower(99);
        $lada->setTransmission('Механика');

        $mercedes->setCarMark($this->getReference('producer_mercedes'));
        $mercedes->setCarModel('SLR McLaren');
        $mercedes->setStateNumber('A444BC');
        $mercedes->setProductionYear(2004);
        $mercedes->setVinNumber('VINMERCEDEC444');
        $mercedes->setImage('mercedes-benz-slr-mclaren-8615164079-6825b3f16f4a2602736041.jpg');
        $mercedes->setIsFree(true);
        $mercedes->setIsActive(true);
        $mercedes->setWeight(1.7);
        $mercedes->setWeightLift(0.250);
        $mercedes->setFuelType('Бензин');
        $mercedes->setFuelingType('ДВС (Двигатель внутреннего сгорания)');
        $mercedes->setPlaces(2);
        $mercedes->setHorsePower(650);
        $mercedes->setTransmission('Механика');

        $renault->setCarMark($this->getReference('producer_renault'));
        $renault->setCarModel('Logan');
        $renault->setStateNumber('A379BC');
        $renault->setProductionYear(2010);
        $renault->setVinNumber('VINRENAULT379');
        $renault->setIsFree(true);
        $renault->setIsActive(true);
        $renault->setWeight(1.5);
        $renault->setWeightLift(0.350);
        $renault->setFuelType('Бензин');
        $renault->setFuelingType('ДВС (Двигатель внутреннего сгорания)');
        $renault->setPlaces(4);
        $renault->setHorsePower(99);
        $renault->setTransmission('Механика');

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
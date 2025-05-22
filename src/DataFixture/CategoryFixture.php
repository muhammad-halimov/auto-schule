<?php

namespace App\DataFixture;

use App\Entity\Category;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class CategoryFixture extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $categoryA = new Category();
        $categoryB = new Category();
        $categoryD = new Category();
        $categoryC = new Category();
        $categoryAalt = new Category();
        $categoryBalt = new Category();
        $categoryArr = [$categoryA, $categoryB, $categoryD, $categoryC];

        $categoryA->setTitle('Категория A');
        $categoryA->setMasterTitle('A');
        $categoryA->setDescription('Категория для мотоциклов. Мотоциклы.');
        $categoryA->setType('driving');
        $categoryA->setPrice(750);

        $categoryB->setTitle('Категория B');
        $categoryB->setMasterTitle('B');
        $categoryB->setDescription('Категория для автомобилей. Легковые авто.');
        $categoryB->addCar($this->getReference('car_lada'));
        $categoryB->addCar($this->getReference('car_renault'));
        $categoryB->addCar($this->getReference('car_mercedes'));
        $categoryB->setType('driving');
        $categoryB->setPrice(750);

        $categoryC->setTitle('Категория C');
        $categoryC->setMasterTitle('C');
        $categoryC->setDescription('Категория для грузовиков. Грузовики и крупногаборитное авто.');
        $categoryC->setType('driving');
        $categoryC->setPrice(1750);

        $categoryD->setTitle('Категория D');
        $categoryD->setMasterTitle('D');
        $categoryD->setDescription('Категория для автобусов. Общественный транспорт.');
        $categoryD->setType('driving');
        $categoryD->setPrice(1750);

        $categoryAalt->setTitle('Категория A');
        $categoryAalt->setMasterTitle('A');
        $categoryAalt->setDescription('Категория для мотоциклов. Мотоциклы.');
        $categoryAalt->setType('course');
        $categoryAalt->setPrice(24500);

        $categoryBalt->setTitle('Категория B');
        $categoryBalt->setMasterTitle('B');
        $categoryBalt->setDescription('Категория для автомобилей. Легковые авто.');
        $categoryBalt->setType('course');
        $categoryBalt->setPrice(24500);

        foreach ($categoryArr as $category) {
            $manager->persist($category);
        }

        $this->addReference('category_a', $categoryA);
        $this->addReference('category_b', $categoryB);
        $this->addReference('category_c', $categoryC);
        $this->addReference('category_d', $categoryD);

        $this->addReference('category_a_alt', $categoryAalt);
        $this->addReference('category_b_alt', $categoryBalt);

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [];
    }
}
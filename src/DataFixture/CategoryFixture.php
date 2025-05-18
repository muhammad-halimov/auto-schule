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
        $categoryArr = [$categoryA, $categoryB, $categoryD, $categoryC];

        $categoryA->setTitle('Категория A');
        $categoryA->setDescription('Категория для мотоциклов. Мотоциклы.');

        $categoryB->setTitle('Категория B');
        $categoryB->setDescription('Категория для автомобилей. Легковые авто.');

        $categoryC->setTitle('Категория C');
        $categoryC->setDescription('Категория для грузовиков. Грузовики и крупногаборитное авто.');

        $categoryD->setTitle('Категория D');
        $categoryD->setDescription('Категория для автобусов. Общественный транспорт.');

        foreach ($categoryArr as $category) {
            $manager->persist($category);
        }

        $this->addReference('category_a', $categoryA);
        $this->addReference('category_b', $categoryB);
        $this->addReference('category_c', $categoryC);
        $this->addReference('category_d', $categoryD);

        $manager->flush();
    }
}
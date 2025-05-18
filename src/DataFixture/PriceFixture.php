<?php

namespace App\DataFixture;

use App\Entity\Price;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class PriceFixture extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $priceCategoryA = new Price();
        $priceCategoryB = new Price();
        $priceCategoryC = new Price();
        $priceCategoryD = new Price();
        $priceCourseA = new Price();
        $priceCourseB = new Price();

        $pricesArr = [
            $priceCategoryA,
            $priceCategoryB,
            $priceCategoryC,
            $priceCategoryD,
            $priceCourseA,
            $priceCourseB
        ];

        $priceCategoryA->setPrice(750);
        $priceCategoryA->setType('driving');
        $priceCategoryA->setCategory($this->getReference('category_a'));

        $priceCategoryB->setPrice(750);
        $priceCategoryB->setType('driving');
        $priceCategoryB->setCategory($this->getReference('category_b'));

        $priceCategoryC->setPrice(1750);
        $priceCategoryC->setType('driving');
        $priceCategoryC->setCategory($this->getReference('category_c'));

        $priceCategoryD->setPrice(1750);
        $priceCategoryD->setType('driving');
        $priceCategoryD->setCategory($this->getReference('category_b'));

        $priceCourseA->setPrice(24750);
        $priceCourseA->setType('course');
        $priceCourseA->setCategory($this->getReference('category_a'));

        $priceCourseB->setPrice(24750);
        $priceCourseB->setType('course');
        $priceCourseB->setCategory($this->getReference('category_b'));

        foreach ($pricesArr as $price) {
            $manager->persist($price);
        }

        $manager->flush();
    }

    public function getDependencies(): array
    {
        return [
            CategoryFixture::class,
        ];
    }
}
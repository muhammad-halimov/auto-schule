<?php

namespace App\Controller\Admin;

use App\Entity\Car;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\AssociationField;
use EasyCorp\Bundle\EasyAdminBundle\Field\BooleanField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IntegerField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextEditorField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;

class CarCrudController extends AbstractCrudController
{
    public static function getEntityFqcn(): string
    {
        return Car::class;
    }

    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityPermission('ROLE_ADMIN')
            ->setEntityLabelInPlural('Автомобили')
            ->setEntityLabelInSingular('автомобиль')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление автомобиля')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение автомобиля')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация об автомобиле");
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')
            ->onlyOnIndex();

        yield TextField::new('carMark', 'Марка авто')
            ->setColumns(5);

        yield TextField::new('carModel', 'Модель авто')
            ->setColumns(5);

        yield TextField::new('stateNumber', 'Гос. номер')
            ->setColumns(5);

        yield TextField::new('vinNumber', 'VIN номер')
            ->setColumns(5);

        yield AssociationField::new('category', 'Категория')
            ->setColumns(5);

        yield DateField::new('productionYear', 'Год производтсва')
            ->setColumns(5);

        yield BooleanField::new('isFree', 'Свободна?')
            ->setColumns(8)
            ->renderAsSwitch();

        yield BooleanField::new('isActive', 'Активная?')
            ->setColumns(8)
            ->renderAsSwitch();
    }
}

<?php

namespace App\Controller\Admin;

use App\Controller\Admin\Field\VichImageField;
use App\Entity\Car;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\AssociationField;
use EasyCorp\Bundle\EasyAdminBundle\Field\BooleanField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IntegerField;
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

        yield AssociationField::new('carMark', 'Марка авто')
            ->setRequired(true)
            ->setColumns(6);

        yield TextField::new('carModel', 'Модель авто')
            ->setRequired(true)
            ->setColumns(6);

        yield TextField::new('stateNumber', 'Гос. номер')
            ->setRequired(true)
            ->setColumns(6);

        yield TextField::new('vinNumber', 'VIN номер')
            ->setRequired(true)
            ->setColumns(6);

        yield AssociationField::new('category', 'Категория')
            ->setRequired(true)
            ->setColumns(6);

        yield IntegerField::new('productionYear', 'Год производства')
            ->setRequired(true)
            ->setColumns(6);

        yield BooleanField::new('isFree', 'Свободна?')
            ->setColumns(8)
            ->addCssClass("form-switch");

        yield BooleanField::new('isActive', 'Активная?')
            ->setColumns(8)
            ->addCssClass("form-switch");

        yield VichImageField::new('imageFile', 'Фото автомобиля')
            ->setHelp('
                <div class="mt-3">
                    <span class="badge badge-info">*.jpg</span>
                    <span class="badge badge-info">*.jpeg</span>
                    <span class="badge badge-info">*.png</span>
                    <span class="badge badge-info">*.jiff</span>
                    <span class="badge badge-info">*.webp</span>
                </div>
            ')
            ->onlyOnForms()
            ->setColumns(5);

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

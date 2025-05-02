<?php

namespace App\Controller\Admin;

use App\Entity\Price;
use EasyCorp\Bundle\EasyAdminBundle\Config\Action;
use EasyCorp\Bundle\EasyAdminBundle\Config\Actions;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\AssociationField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IntegerField;

class PriceCrudController extends AbstractCrudController
{
    public static function getEntityFqcn(): string
    {
        return Price::class;
    }

    /**
     * @IsGranted("ROLE_ADMIN")
     * @IsGranted("ROLE_INSTRUCTOR")
     */
    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityLabelInPlural('Цены')
            ->setEntityLabelInSingular('цену')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление цены')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение цены')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация о цене");
    }

    public function configureActions(Actions $actions): Actions
    {
        return parent::configureActions($actions)
            ->setPermissions([
                Action::NEW => 'ROLE_ADMIN',
                Action::DELETE => 'ROLE_ADMIN',
                Action::EDIT => 'ROLE_ADMIN',
            ]);
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')->onlyOnIndex();

        yield IntegerField::new('price', 'Цена')
            ->setRequired(true)
            ->setColumns(6);

        yield AssociationField::new('category', 'Категория')
            ->setRequired(true)
            ->setColumns(6);

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

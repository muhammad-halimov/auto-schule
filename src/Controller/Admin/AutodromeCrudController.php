<?php

namespace App\Controller\Admin;

use App\Entity\Autodrome;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextEditorField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;

class AutodromeCrudController extends AbstractCrudController
{
    public static function getEntityFqcn(): string
    {
        return Autodrome::class;
    }

    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityPermission('ROLE_ADMIN')
            ->setEntityLabelInPlural('Автодромы')
            ->setEntityLabelInSingular('автодром')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление автодрома')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение автодрома')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация об автодроме");
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')
            ->onlyOnIndex();

        yield TextField::new('title', 'Автодром')
            ->setColumns(6);

        yield TextField::new('address', 'Адрес')
            ->setColumns(6);

        yield TextEditorField::new('description', 'Описание')
            ->setColumns(12);

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

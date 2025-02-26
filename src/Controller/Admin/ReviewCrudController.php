<?php

namespace App\Controller\Admin;

use App\Entity\Review;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\AssociationField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextEditorField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;

class ReviewCrudController extends AbstractCrudController
{
    public static function getEntityFqcn(): string
    {
        return Review::class;
    }

    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityPermission('ROLE_ADMIN')
            ->setEntityLabelInPlural('Отзывы')
            ->setEntityLabelInSingular('отзыв')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление отзыва')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение отзыва')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация об отзыве");
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')
            ->onlyOnIndex();

        yield TextField::new('title', 'Названние')
            ->setColumns(4);

        yield TextField::new('category', 'Категория')
            ->setColumns(4);

        yield AssociationField::new('publisher', 'Автор')
            ->setColumns(4);

        yield TextEditorField::new('description', 'Описание')
            ->setColumns(12);
    }
}

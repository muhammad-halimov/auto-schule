<?php

namespace App\Controller\Admin;

use App\Entity\AutoProducer;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextEditorField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;

class AutoProducerCrudController extends AbstractCrudController
{
    public static function getEntityFqcn(): string
    {
        return AutoProducer::class;
    }

    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityPermission('ROLE_ADMIN')
            ->setEntityLabelInPlural('Автопроизводители')
            ->setEntityLabelInSingular('автопроизводителя')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление автопроизводителя')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение автопроизводителя')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация об автопроизводителе");
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')
            ->onlyOnIndex();

        yield TextField::new('title', 'Название')
            ->setRequired(true)
            ->setColumns(4);

        yield TextField::new('headquarters', 'Страна')
            ->setRequired(true)
            ->setColumns(4);

        yield DateField::new('established', 'Основано')
            ->setRequired(true)
            ->setColumns(4);

        yield TextEditorField::new('description', 'Описание')
            ->setRequired(false)
            ->setColumns(9);

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

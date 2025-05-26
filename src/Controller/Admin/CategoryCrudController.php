<?php

namespace App\Controller\Admin;

use App\Entity\Category;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\ChoiceField;
use EasyCorp\Bundle\EasyAdminBundle\Field\CollectionField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IntegerField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextEditorField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;

class CategoryCrudController extends AbstractCrudController
{
    public static function getEntityFqcn(): string
    {
        return Category::class;
    }

    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityPermission('ROLE_ADMIN')
            ->setEntityLabelInPlural('Категории')
            ->setEntityLabelInSingular('категорию')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление категории')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение категории')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация о категории");
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')
            ->onlyOnIndex();

        yield TextField::new('title', 'Наименование')
            ->setRequired(true)
            ->setColumns(3);

        yield ChoiceField::new('masterTitle', 'Категория')
            ->setChoices([
                'A'  => 'A',
                'A1' => 'A1',
                'B'  => 'B',
                'B1' => 'B1',
                'C'  => 'C',
                'C1' => 'C1',
                'D'  => 'D',
                'D1' => 'D1',
                'BE' => 'BE',
                'CE' => 'CE',
                'C1E' => 'C1E',
                'DE' => 'DE',
                'D1E' => 'D1E',
                'M'  => 'M',
                'Tb'  => 'Tb',
                'Tm'  => 'Tm',
            ])
            ->setRequired(true)
            ->setColumns(3);

        yield IntegerField::new('price', 'Цена')
            ->setRequired(true)
            ->setColumns(3);

        yield ChoiceField::new('type', 'Тип')
            ->setChoices([
                'Курс' => "course",
                'Вождение' => "driving",
            ])
            ->setRequired(true)
            ->setColumns(3);

        yield TextEditorField::new('description', 'Описание')
            ->setColumns(12);

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

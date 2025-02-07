<?php

namespace App\Controller\Admin;

use App\Entity\Course;
use App\Entity\TeacherLesson;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\AssociationField;
use EasyCorp\Bundle\EasyAdminBundle\Field\CollectionField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextEditorField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;

class CourseCrudController extends AbstractCrudController
{
    public static function getEntityFqcn(): string
    {
        return Course::class;
    }

    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityPermission('ROLE_ADMIN')
            ->setEntityLabelInPlural('Курсы')
            ->setEntityLabelInSingular('курс')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление курса')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение курса')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация о курсе");
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')->onlyOnIndex();

        yield TextField::new('title', 'Название')
            ->setColumns(6)
            ->setRequired(true);

        yield AssociationField::new('lessons', 'Занятия')
            ->setColumns(6);

        yield TextEditorField::new('description', 'Описание')
            ->setColumns(12)
            ->setRequired(true);

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

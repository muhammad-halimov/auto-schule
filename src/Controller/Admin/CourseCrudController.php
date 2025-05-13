<?php

namespace App\Controller\Admin;

use App\Entity\Course;
use Doctrine\ORM\QueryBuilder;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\AssociationField;
use EasyCorp\Bundle\EasyAdminBundle\Field\CollectionField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IntegerField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextEditorField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;

class CourseCrudController extends AbstractCrudController
{
    public static function getEntityFqcn(): string
    {
        return Course::class;
    }

    /**
     * @IsGranted("ROLE_ADMIN")
     * @IsGranted("ROLE_TEACHER")
     */
    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityLabelInPlural('Курсы')
            ->setEntityLabelInSingular('курс')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление курса')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение курса')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация о курсе");
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')->onlyOnIndex();

        yield AssociationField::new('users', 'Студенты')
            ->setFormTypeOption("by_reference", false)
            ->setQueryBuilder(function (QueryBuilder $qb) {
                return $qb
                    ->andWhere("entity.roles LIKE :role")
                    ->andWhere("entity.isActive = :active")
                    ->andWhere("entity.isApproved = :approved")
                    ->setParameter('role', '%ROLE_STUDENT%')
                    ->setParameter('active', true)
                    ->setParameter('approved', true);
            })
            ->setColumns(3);

        yield TextField::new('title', 'Название')
            ->setColumns(3)
            ->setRequired(true);

        yield AssociationField::new('category', 'Категория')
            ->setRequired(true)
            ->setColumns(3);

        yield IntegerField::new('price', 'Цена')
            ->setRequired(true)
            ->setColumns(3);

        yield CollectionField::new('lessons', 'Занятия')
            ->useEntryCrudForm(TeacherLessonCrudController::class)
            ->setColumns(12);

        yield CollectionField::new('courseQuizzes', 'Тесты')
            ->useEntryCrudForm(CourseQuizCrudController::class)
            ->onlyOnForms()
            ->setColumns(12);

        yield TextEditorField::new('description', 'Описание')
            ->setColumns(12);

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

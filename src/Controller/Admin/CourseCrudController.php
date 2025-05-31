<?php

namespace App\Controller\Admin;

use App\Entity\Course;
use Doctrine\ORM\QueryBuilder;
use EasyCorp\Bundle\EasyAdminBundle\Config\Action;
use EasyCorp\Bundle\EasyAdminBundle\Config\Actions;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\AssociationField;
use EasyCorp\Bundle\EasyAdminBundle\Field\CollectionField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IntegerField;
use EasyCorp\Bundle\EasyAdminBundle\Field\MoneyField;
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

    public function configureActions(Actions $actions): Actions
    {
        $actions
            ->add(Crud::PAGE_INDEX, Action::DETAIL);

        return parent::configureActions($actions);
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id', "ID")
            ->hideOnForm();

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
            ->setColumns(4);

        yield TextField::new('title', 'Название')
            ->setColumns(4)
            ->setRequired(true);

        yield AssociationField::new('category', 'Категория')
            ->setQueryBuilder(function (QueryBuilder $qb) {
                return $qb
                    ->andWhere("entity.type LIKE :type")
                    ->setParameter('type', 'course');
            })
            ->setRequired(true)
            ->setColumns(4);

        yield IntegerField::new('lessonsCount', 'Кол-во занятий')
            ->hideOnForm();

        yield IntegerField::new('courseQuizzesCount', 'Кол-во тестов')
            ->hideOnForm();

        yield CollectionField::new('lessons', 'Занятия')
            ->hideOnIndex()
            ->useEntryCrudForm(TeacherLessonCrudController::class)
            ->setColumns(12);

        yield CollectionField::new('courseQuizzes', 'Тесты')
            ->hideOnIndex()
            ->useEntryCrudForm(CourseQuizCrudController::class)
            ->setColumns(12);

        yield TextEditorField::new('description', 'Описание')
            ->setColumns(12);

        yield MoneyField::new('category.price', 'Цена')
            ->setCurrency('RUB')
            ->setStoredAsCents(false)
            ->onlyOnIndex();

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

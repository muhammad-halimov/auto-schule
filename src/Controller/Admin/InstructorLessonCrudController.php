<?php

namespace App\Controller\Admin;

use App\Entity\InstructorLesson;
use Doctrine\ORM\QueryBuilder;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\AssociationField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IntegerField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;

class InstructorLessonCrudController extends AbstractCrudController
{
    public static function getEntityFqcn(): string
    {
        return InstructorLesson::class;
    }

    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityPermission('ROLE_ADMIN')
            ->setEntityLabelInPlural('Уроки вождения')
            ->setEntityLabelInSingular('урок вождения')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление урока вождения')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение урока вождения')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация об уроке вождении");
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')->onlyOnIndex();

        yield TextField::new('title', 'Название')
            ->setColumns(6)
            ->setRequired(true);

        yield IntegerField::new('price', 'Цена')
            ->setColumns(6)
            ->setRequired(true);

        yield AssociationField::new('instructor', 'Инструктор')
            ->setQueryBuilder(function (QueryBuilder $qb) {
                return $qb
                    ->andWhere("entity.roles LIKE :role")
                    ->andWhere("entity.isActive = :active")
                    ->andWhere("entity.isApproved = :approved")
                    ->setParameter('role', '%ROLE_INSTRUCTOR%')
                    ->setParameter('active', true)
                    ->setParameter('approved', true);
            })
            ->setColumns(6);

        yield AssociationField::new('student', 'Студент')
            ->setQueryBuilder(function (QueryBuilder $qb) {
                return $qb
                    ->where("entity.roles LIKE :role")
                    ->setParameter('role', '%ROLE_STUDENT%');
            })
            ->setColumns(6);

        yield DateTimeField::new('date', 'Дата и время')
            ->setColumns(4);

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

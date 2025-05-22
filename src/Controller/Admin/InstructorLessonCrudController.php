<?php

namespace App\Controller\Admin;

use App\Entity\InstructorLesson;
use App\Repository\CategoryRepository;
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

    /**
     * @IsGranted("ROLE_ADMIN")
     * @IsGranted("ROLE_INSTRUCTOR")
     */
    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityLabelInPlural('Уроки вождения')
            ->setEntityLabelInSingular('урок вождения')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление урока вождения')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение урока вождения')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация об уроке вождении");
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')
            ->hideOnForm();

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
            ->setRequired(true)
            ->setQueryBuilder(function (QueryBuilder $qb) {
                return $qb
                    ->andWhere("entity.roles LIKE :role")
                    ->andWhere("entity.isActive = :active")
                    ->andWhere("entity.isApproved = :approved")
                    ->setParameter('role', '%ROLE_STUDENT%')
                    ->setParameter('active', true)
                    ->setParameter('approved', true);
            })
            ->setColumns(6);

        yield AssociationField::new('autodrome', 'Автодром')
            ->setRequired(true)
            ->setColumns(6);

//        yield AssociationField::new('category', 'Категория')
//            ->setFormTypeOptions([
//                'query_builder' => function (CategoryRepository $repo) {
//                    return $repo->createQueryBuilder('c')
//                        ->join('c.price', 'p')
//                        ->andWhere('p.type = :type')
//                        ->setParameter('type', 'driving');
//                }
//            ])
//            ->setColumns(6);

        yield AssociationField::new('category', 'Категория')
            ->setQueryBuilder(function (QueryBuilder $qb) {
                return $qb
                    ->andWhere("entity.type LIKE :type")
                    ->setParameter('type', 'driving');
            })
            ->setColumns(6);

        yield DateTimeField::new('date', 'Дата и время')
            ->setRequired(true)
            ->setColumns(4);

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

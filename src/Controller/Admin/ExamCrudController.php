<?php

namespace App\Controller\Admin;

use App\Entity\Exam;
use Doctrine\ORM\QueryBuilder;
use EasyCorp\Bundle\EasyAdminBundle\Config\Action;
use EasyCorp\Bundle\EasyAdminBundle\Config\Actions;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\AssociationField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\MoneyField;

class ExamCrudController extends AbstractCrudController
{
    public static function getEntityFqcn(): string
    {
        return Exam::class;
    }

    public function configureActions(Actions $actions): Actions
    {
        $actions->add(Crud::PAGE_INDEX, Action::DETAIL);

        return parent::configureActions($actions);
    }

    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityPermission('ROLE_ADMIN')
            ->setEntityLabelInPlural('Экзамены')
            ->setEntityLabelInSingular('экзамен')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление экзамена')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение экзамена')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация об экзамене");
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')
            ->onlyOnIndex();

        yield AssociationField::new('students', 'Студенты')
            ->setRequired(true)
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
            ->setColumns(6);

        yield AssociationField::new('categories', 'Категория')
            ->setQueryBuilder(function (QueryBuilder $qb) {
                return $qb
                    ->andWhere("entity.type LIKE :type")
                    ->setParameter('type', 'driving');
            })
            ->setFormTypeOption("by_reference", false)
            ->setColumns(6);

        yield AssociationField::new('autodrome', 'Автодром')
            ->setRequired(true)
            ->setColumns(6);

        yield DateTimeField::new('date', 'Дата и время')
            ->setRequired(true)
            ->setColumns(6);

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

<?php

namespace App\Controller\Admin;

use App\Entity\DriveSchedule;
use Doctrine\ORM\QueryBuilder;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\AssociationField;
use EasyCorp\Bundle\EasyAdminBundle\Field\ChoiceField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextEditorField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TimeField;

class DriveScheduleCrudController extends AbstractCrudController
{
    public static function getEntityFqcn(): string
    {
        return DriveSchedule::class;
    }

    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityPermission('ROLE_ADMIN')
            ->setEntityLabelInPlural('Расписание')
            ->setEntityLabelInSingular('расписание')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление расписания')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение расписания')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация о расписаниях");
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')
            ->onlyOnIndex();

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

        yield ChoiceField::new('daysOfWeek', 'Дни недели')
            ->setChoices([
                'Пн - Понедельник' => "Пн - Понедельник",
                'Вт - Вторник' => "Вт - Вторник",
                'Ср - Среда' => 'Ср - Среда',
                'Чт - Четверг' => 'Чт - Четверг',
                'Пт - Пятница' => 'Пт - Пятница',
                'Сб - Суббота' => 'Сб - Суббота',
                'Вс - Воскресенье' => 'Вс - Воскресенье',
            ])
            ->allowMultipleChoices(true)
            ->setColumns(6);

        yield TimeField::new('timeFrom', 'Время от')
            ->setColumns(1);

        yield TimeField::new('timeTo', 'Время до')
            ->setColumns(1);

        yield TextEditorField::new('notice', 'Замечание')
            ->setColumns(12);
    }
}

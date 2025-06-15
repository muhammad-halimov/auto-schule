<?php

namespace App\Controller\Admin;

use App\Entity\DriveSchedule;
use Doctrine\ORM\QueryBuilder;
use EasyCorp\Bundle\EasyAdminBundle\Config\Action;
use EasyCorp\Bundle\EasyAdminBundle\Config\Actions;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\AssociationField;
use EasyCorp\Bundle\EasyAdminBundle\Field\ChoiceField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IntegerField;
use EasyCorp\Bundle\EasyAdminBundle\Field\MoneyField;
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

    public function configureActions(Actions $actions): Actions
    {
        $actions->add(Crud::PAGE_INDEX, Action::DETAIL);

        return parent::configureActions($actions);
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
                'Пн' => "Пн",
                'Вт' => "Вт",
                'Ср' => 'Ср',
                'Чт' => 'Чт',
                'Пт' => 'Пт',
                'Сб' => 'Сб',
            ])
            ->allowMultipleChoices(true)
            ->setColumns(6);

        yield IntegerField::new('daysOfWeekCount', 'Кол-во дней')
            ->hideOnForm();

        yield AssociationField::new('autodrome', 'Автодром')
            ->setColumns(6);

        # TODO: Пофиксить фильтр для категорий, он должен стоять в зависимости от инструктора
        yield AssociationField::new('category', 'Категория')
            ->setQueryBuilder(function (QueryBuilder $qb) {
                return $qb
                    ->andWhere("entity.type LIKE :type")
                    ->setParameter('type', 'driving');
            })
            ->setColumns(6);

        yield TimeField::new('timeFrom', 'Время от')
            ->renderAsNativeWidget(true)
            ->setColumns(2);

        yield TimeField::new('timeTo', 'Время до')
            ->renderAsNativeWidget(true)
            ->setColumns(2);

        yield MoneyField::new('category.price', 'Цена')
            ->setCurrency('RUB')
            ->setStoredAsCents(false)
            ->onlyOnIndex();

        yield TextEditorField::new('notice', 'Замечание')
            ->setColumns(12);

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

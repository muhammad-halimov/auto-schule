<?php

namespace App\Controller\Admin;

use App\Controller\Admin\Field\VichImageField;
use App\Entity\Review;
use Doctrine\ORM\QueryBuilder;
use EasyCorp\Bundle\EasyAdminBundle\Config\Action;
use EasyCorp\Bundle\EasyAdminBundle\Config\Actions;
use EasyCorp\Bundle\EasyAdminBundle\Config\Assets;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\AssociationField;
use EasyCorp\Bundle\EasyAdminBundle\Field\ChoiceField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextEditorField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;

class ReviewCrudController extends AbstractCrudController
{
    public static function getEntityFqcn(): string
    {
        return Review::class;
    }

    public function configureAssets(Assets $assets): Assets
    {
        return parent::configureAssets($assets)
            ->addJsFile("assets/js/reviewCrud.js");
    }

    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityPermission('ROLE_ADMIN')
            ->setEntityLabelInPlural('Отзывы')
            ->setEntityLabelInSingular('отзыв')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление отзыва')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение отзыва')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация об отзыве");
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

        yield ChoiceField::new('type', 'Тип отзыва')
            ->setRequired(true)
            ->renderExpanded()
            ->addCssClass("form-switch")
            ->setChoices([
                'Курс' => "course",
                'Представитель' => "representative",
            ])
            ->setColumns(12);

        yield TextField::new('title', 'Названние')
            ->setRequired(true)
            ->setColumns(3);

        yield AssociationField::new('course', 'Курс')
            ->setRequired(true)
            ->addCssClass("course-field")
            ->setColumns(3);

        yield AssociationField::new('representativeFigure', 'Инструктор / Преподаватель')
            ->setRequired(true)
            ->setQueryBuilder(function (QueryBuilder $qb) {
                return $qb
                    ->andWhere("entity.roles LIKE :teacherRole OR entity.roles LIKE :instructorRole")
                    ->andWhere("entity.isActive = :active")
                    ->andWhere("entity.isApproved = :approved")
                    ->setParameter('active', true)
                    ->setParameter('approved', true)
                    ->setParameter('teacherRole', '%ROLE_TEACHER%')
                    ->setParameter('instructorRole', '%ROLE_INSTRUCTOR%');
            })
            ->addCssClass("representative-field")
            ->setColumns(3);

        yield AssociationField::new('publisher', 'Автор')
            ->setRequired(true)
            ->setQueryBuilder(function (QueryBuilder $qb) {
                return $qb
                    ->andWhere("entity.roles LIKE :role")
                    ->andWhere("entity.isActive = :active")
                    ->andWhere("entity.isApproved = :approved")
                    ->setParameter('active', true)
                    ->setParameter('approved', true)
                    ->setParameter('role', ('%ROLE_STUDENT%'));
            })
            ->setColumns(3);

        yield TextEditorField::new('description', 'Описание')
            ->setRequired(true)
            ->setColumns(12);

        yield VichImageField::new('imageFile', 'Изображение')
            ->setHelp('
                <div class="mt-3">
                    <span class="badge badge-info">*.jpg</span>
                    <span class="badge badge-info">*.jpeg</span>
                    <span class="badge badge-info">*.png</span>
                    <span class="badge badge-info">*.jiff</span>
                    <span class="badge badge-info">*.webp</span>
                </div>
            ')
            ->onlyOnForms()
            ->setColumns(12);

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

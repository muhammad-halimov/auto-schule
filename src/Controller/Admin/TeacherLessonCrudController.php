<?php

namespace App\Controller\Admin;

use App\Entity\TeacherLesson;
use Doctrine\ORM\QueryBuilder;
use EasyCorp\Bundle\EasyAdminBundle\Config\Action;
use EasyCorp\Bundle\EasyAdminBundle\Config\Actions;
use EasyCorp\Bundle\EasyAdminBundle\Config\Assets;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\AssociationField;
use EasyCorp\Bundle\EasyAdminBundle\Field\ChoiceField;
use EasyCorp\Bundle\EasyAdminBundle\Field\CollectionField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IntegerField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextEditorField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;

class TeacherLessonCrudController extends AbstractCrudController
{
    public static function getEntityFqcn(): string
    {
        return TeacherLesson::class;
    }

    public function configureAssets(Assets $assets): Assets
    {
        return parent::configureAssets($assets)
            ->addJsFile("assets/js/teacherLessonCrud.js");
    }

    /**
     * @IsGranted("ROLE_ADMIN")
     * @IsGranted("ROLE_TEACHER")
     */
    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityLabelInPlural('Занятия')
            ->setEntityLabelInSingular('занятие')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление занятия')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение занятия')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация о занятии");
    }

    public function configureActions(Actions $actions): Actions
    {
        $actions
            ->add(Crud::PAGE_INDEX, Action::DETAIL)
            ->remove(Crud::PAGE_INDEX, Action::NEW)
            ->remove(Crud::PAGE_INDEX, Action::EDIT)
            ->remove(Crud::PAGE_DETAIL, Action::EDIT);

        return parent::configureActions($actions);
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id', 'ID')
            ->hideOnForm();

        yield TextField::new('title', 'Название')
            ->setColumns(6)
            ->setRequired(true);

        yield AssociationField::new('teacher', 'Преподаватель')
            ->setRequired(true)
            ->setQueryBuilder(function (QueryBuilder $qb) {
                return $qb
                    ->andWhere("entity.roles LIKE :role")
                    ->andWhere("entity.isActive = :active")
                    ->andWhere("entity.isApproved = :approved")
                    ->setParameter('role', '%ROLE_TEACHER%')
                    ->setParameter('active', true)
                    ->setParameter('approved', true);
            })
            ->setColumns(6);

        yield AssociationField::new('course', 'Курс')
            ->onlyOnIndex();

        yield CollectionField::new('videos', 'Видео')
            ->hideOnIndex()
            ->useEntryCrudForm(TeacherLessonVideoCrudController::class)
            ->setColumns(6);

        yield IntegerField::new('orderNumber', 'Занятие №')
            ->setRequired(true)
            ->setColumns(4);

        yield ChoiceField::new('type', 'Тип')
            ->setChoices([
                "Онлайн" => "online",
                "Офлайн" => "offline",
            ])
            ->setRequired(true)
            ->setColumns(2);

        yield DateTimeField::new('date', 'Дата и время')
            ->setRequired(false)
            ->setColumns(12)
            ->setRequired(true);

        yield TextEditorField::new('description', 'Описание урока')
            ->setRequired(false)
            ->onlyOnForms()
            ->setColumns(12);

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

<?php

namespace App\Controller\Admin;

use App\Entity\TeacherLesson;
use App\Entity\TeacherLessonVideo;
use Doctrine\ORM\QueryBuilder;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\AssociationField;
use EasyCorp\Bundle\EasyAdminBundle\Field\CollectionField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;

class TeacherLessonCrudController extends AbstractCrudController
{
    public static function getEntityFqcn(): string
    {
        return TeacherLesson::class;
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

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')
            ->onlyOnIndex();

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

        yield CollectionField::new('videos', 'Видео')
            ->onlyOnForms()
            ->useEntryCrudForm(TeacherLessonVideoCrudController::class)
            ->setColumns(6);

        yield DateTimeField::new('date', 'Дата и время')
            ->setColumns(6)
            ->setRequired(true);

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

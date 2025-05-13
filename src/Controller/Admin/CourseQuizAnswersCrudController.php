<?php

namespace App\Controller\Admin;

use App\Entity\CourseQuizAnswers;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\BooleanField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextEditorField;

class CourseQuizAnswersCrudController extends AbstractCrudController
{
    public static function getEntityFqcn(): string
    {
        return CourseQuizAnswers::class;
    }

    /**
     * @IsGranted("ROLE_ADMIN")
     * @IsGranted("ROLE_TEACHER")
     */
    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityLabelInPlural('Отвветы')
            ->setEntityLabelInSingular('ответ')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление ответа')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение ответа')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация об ответе");
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')
            ->onlyOnIndex();

        yield TextEditorField::new('answerText', 'Ответ')
            ->setColumns(12)
            ->setRequired(true);

        yield BooleanField::new('status', 'Статус')
            ->setColumns(12)
            ->setRequired(true)
            ->addCssClass("form-switch");
    }
}
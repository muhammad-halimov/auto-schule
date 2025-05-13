<?php

namespace App\Controller\Admin;

use App\Entity\CourseQuiz;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\CollectionField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextEditorField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;

class CourseQuizCrudController extends AbstractCrudController
{
    public static function getEntityFqcn(): string
    {
        return CourseQuiz::class;
    }

    /**
     * @IsGranted("ROLE_ADMIN")
     * @IsGranted("ROLE_TEACHER")
     */
    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityLabelInPlural('Тесты')
            ->setEntityLabelInSingular('тест')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление теста')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение теста')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация о тесте");
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')->onlyOnIndex();

        yield TextField::new('question', 'Вопрос')
            ->setColumns(12)
            ->setRequired(true);

        yield CollectionField::new('answers', 'Ответы')
            ->setColumns(12)
            ->useEntryCrudForm(CourseQuizAnswersCrudController::class)
            ->setRequired(true);
    }
}

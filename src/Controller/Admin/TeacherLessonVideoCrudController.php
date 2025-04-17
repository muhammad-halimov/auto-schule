<?php

namespace App\Controller\Admin;

use App\Controller\Admin\Field\VichFileField;
use App\Entity\TeacherLessonVideo;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;

class TeacherLessonVideoCrudController extends AbstractCrudController
{
    public static function getEntityFqcn(): string
    {
        return TeacherLessonVideo::class;
    }

    /**
     * @IsGranted("ROLE_ADMIN")
     * @IsGranted("ROLE_TEACHER")
     */
    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityLabelInPlural('Видео')
            ->setEntityLabelInSingular('видео')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление видео')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение видео')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация о видео");
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')
            ->onlyOnIndex();

        yield TextField::new('title', 'Название')
            ->setColumns(12)
            ->setRequired(true);

        yield VichFileField::new('videoFile', 'Видео')
            ->setHelp('
                <div class="mt-3">
                    <span class="badge badge-info">*.mp4</span>
                    <span class="badge badge-info">*.webm</span>
                    <span class="badge badge-info">*.avi</span>
                </div>')
            ->onlyOnForms();
    }
}

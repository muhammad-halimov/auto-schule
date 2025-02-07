<?php

namespace App\Controller\Admin;

use App\Entity\Instructor;
use Doctrine\ORM\EntityManagerInterface;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;

class InstructorCrudController extends AbstractCrudController
{
    private UserPasswordHasherInterface $passwordEncoder;

    public function __construct(UserPasswordHasherInterface $passwordEncoder)
    {
        $this->passwordEncoder = $passwordEncoder;
    }

    public static function getEntityFqcn(): string
    {
        return Instructor::class;
    }

    public function persistEntity(EntityManagerInterface $entityManager, $entityInstance): void
    {
        if ($entityInstance instanceof Instructor && $entityInstance->getPlainPassword()) {
            $this->addFlash('notice', 'Пароль изменен и сохранен!');
            $entityInstance->setPassword($this->passwordEncoder->hashPassword($entityInstance, $entityInstance->getPlainPassword()));
        }

        parent::persistEntity($entityManager, $entityInstance);
    }

    public function updateEntity(EntityManagerInterface $entityManager, $entityInstance): void
    {
        if ($entityInstance instanceof Instructor && $entityInstance->getPlainPassword()) {
            $this->addFlash('notice', 'Пароль изменен и сохранен!');
            $entityInstance->setPassword($this->passwordEncoder->hashPassword($entityInstance, $entityInstance->getPlainPassword()));
        }

        parent::updateEntity($entityManager, $entityInstance);
    }

    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityPermission('ROLE_ADMIN')
            ->setEntityLabelInPlural('Инструкторы')
            ->setEntityLabelInSingular('инструктора')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление инструктора')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение инструктора')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация об инструкторе");
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')->onlyOnIndex();

        yield TextField::new('username', 'Логин')
            ->setColumns(3)
            ->setRequired(true);

        yield TextField::new('name', 'Имя')
            ->setColumns(3)
            ->setRequired(true);

        yield TextField::new('surname', 'Фамилия')
            ->setColumns(3)
            ->setRequired(true);

        yield TextField::new('patronym', 'Отчество')
            ->setColumns(3);

        yield TextField::new('stateNumber', 'Гос. номер')
            ->setColumns(6)
            ->setRequired(true);

        yield TextField::new('license', 'Лицензия')
            ->setColumns(6)
            ->setRequired(true);

        yield TextField::new('carMark', 'Марка авто')
            ->setColumns(4)
            ->setRequired(true);

        yield TextField::new('carModel', 'Модель авто')
            ->setColumns(4)
            ->setRequired(true);

        $plainPassword = TextField::new('plainPassword')
            ->setRequired(false)
            ->onlyOnForms();

        if (crud::PAGE_NEW === $pageName) {
            $plainPassword->setLabel('Пароль')
                ->setRequired(true)
                ->setColumns(4);
        }
        else {
            $plainPassword->setLabel('Новый пароль')
                ->setColumns(4);
        }

        yield $plainPassword;

        yield DateTimeField::new('updatedAt', 'Обновлен')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создан')
            ->onlyOnIndex();
    }
}

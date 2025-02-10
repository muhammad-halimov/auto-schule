<?php

namespace App\Controller\Admin;

use App\Entity\User;
use Doctrine\ORM\EntityManagerInterface;
use EasyCorp\Bundle\EasyAdminBundle\Config\Action;
use EasyCorp\Bundle\EasyAdminBundle\Config\Actions;
use EasyCorp\Bundle\EasyAdminBundle\Config\Assets;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\BooleanField;
use EasyCorp\Bundle\EasyAdminBundle\Field\ChoiceField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\EmailField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;

class UserCrudController extends AbstractCrudController
{
    public function configureAssets(Assets $assets): Assets
    {
        return parent::configureAssets($assets)
            ->addJsFile("assets/js/userCrud.js");
    }

    private UserPasswordHasherInterface $passwordEncoder;

    public static function getEntityFqcn(): string
    {
        return User::class;
    }

    public function __construct(UserPasswordHasherInterface $passwordEncoder)
    {
        $this->passwordEncoder = $passwordEncoder;
    }

    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityPermission('ROLE_ADMIN')
            ->setEntityLabelInPlural('Пользователи')
            ->setEntityLabelInSingular('пользователя')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление пользователя')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение пользователя')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация о пользователе");
    }


    public function configureActions(Actions $actions): Actions
    {
        $actions->add(Crud::PAGE_INDEX, Action::DETAIL);
        return parent::configureActions($actions)
            ->setPermissions(
                [
                    Action::NEW => 'ROLE_ADMIN',
                    Action::DELETE => 'ROLE_ADMIN',
                    Action::EDIT => 'ROLE_ADMIN',
                ]);
    }

    public function persistEntity(EntityManagerInterface $entityManager, $entityInstance): void
    {
        if ($entityInstance instanceof User && $entityInstance->getPlainPassword()) {
            $this->addFlash('notice', 'Пароль изменен и сохранен!');
            $entityInstance->setPassword($this->passwordEncoder->hashPassword($entityInstance, $entityInstance->getPlainPassword()));
        }

        parent::persistEntity($entityManager, $entityInstance);
    }

    public function updateEntity(EntityManagerInterface $entityManager, $entityInstance): void
    {
        if ($entityInstance instanceof User && $entityInstance->getPlainPassword()) {
            $this->addFlash('notice', 'Пароль изменен и сохранен!');
            $entityInstance->setPassword($this->passwordEncoder->hashPassword($entityInstance, $entityInstance->getPlainPassword()));
        }

        parent::updateEntity($entityManager, $entityInstance);
    }

    public function configureFields(string $pageName): iterable
    {
        yield IdField::new('id')
            ->onlyOnIndex();

        yield ChoiceField::new('roles', 'Права')
            ->setRequired(true)
            ->allowMultipleChoices()
            ->renderExpanded()
            ->setChoices(User::ROLES)
            ->setColumns(9);

        yield BooleanField::new('examStatus', 'Экзамен сдан?')
            ->setColumns(9)
            ->renderAsSwitch()
            ->onlyOnForms();

        yield TextField::new('username', 'Логин')
            ->setColumns(4)
            ->setRequired(true);

        yield TextField::new('name', 'Имя')
            ->setColumns(4)
            ->setRequired(true);

        yield TextField::new('surname', 'Фамилия')
            ->setColumns(4)
            ->setRequired(true);

        yield TextField::new('patronym', 'Отчество')
            ->setColumns(4);

        yield TextField::new('phone', 'Телефон')
            ->setColumns(4)
            ->setRequired(true);

        yield EmailField::new('email', 'Эл. почта')
            ->setColumns(4)
            ->setRequired(true);

        yield TextField::new('contract', 'Договор')
            ->setColumns(4)
            ->onlyOnForms()
            ->setRequired(true);

        yield TextField::new('carMark', 'Марка Авто')
            ->setColumns(4)
            ->onlyOnForms()
            ->setRequired(true);

        yield TextField::new('carModel', 'Модель Авто')
            ->setColumns(4)
            ->onlyOnForms()
            ->setRequired(true);

        yield TextField::new('stateNumber', 'Гос. номер')
            ->setColumns(4)
            ->onlyOnForms()
            ->setRequired(true);

        yield TextField::new('license', 'Лицензия')
            ->setColumns(4)
            ->onlyOnForms()
            ->setRequired(true);

        yield TextField::new('classTitle', 'Название предмета')
            ->setColumns(4)
            ->onlyOnForms()
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

        yield DateTimeField::new('dateOfBirth', 'Дата рождения')
            ->setColumns(2)
            ->onlyOnForms()
            ->setRequired(true);

        yield DateTimeField::new('hireDate', 'Дата найма')
            ->setColumns(2)
            ->onlyOnForms()
            ->setRequired(true);

        yield DateTimeField::new('enrollDate', 'Дата поступления')
            ->setColumns(2)
            ->onlyOnForms()
            ->setRequired(true);

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

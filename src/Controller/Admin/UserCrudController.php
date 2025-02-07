<?php

namespace App\Controller\Admin;

use App\Entity\User;
use App\Repository\UserRepository;
use Doctrine\ORM\EntityManagerInterface;
use EasyCorp\Bundle\EasyAdminBundle\Config\Action;
use EasyCorp\Bundle\EasyAdminBundle\Config\Actions;
use EasyCorp\Bundle\EasyAdminBundle\Config\Assets;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\AssociationField;
use EasyCorp\Bundle\EasyAdminBundle\Field\BooleanField;
use EasyCorp\Bundle\EasyAdminBundle\Field\ChoiceField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\EmailField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;

class UserCrudController extends AbstractCrudController
{
    private UserRepository $userRepository;

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

    public function __construct(UserPasswordHasherInterface $passwordEncoder, UserRepository $repository)
    {
        $this->passwordEncoder = $passwordEncoder;
        $this->userRepository = $repository;
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
            ->setColumns(9)
            ->setRequired(true);

        yield ChoiceField::new('roles', 'Права')
            ->setRequired(true)
            ->allowMultipleChoices()
            ->renderExpanded()
            ->setChoices(User::ROLES)
            ->setColumns(8)
            ->onlyOnForms();

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

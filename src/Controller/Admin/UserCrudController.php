<?php

namespace App\Controller\Admin;

use App\Entity\User;
use App\Service\ApproveUserRequest;
use App\Service\NewPasswordUserRequest;
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
use EasyCorp\Bundle\EasyAdminBundle\Field\TextEditorField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;
use EasyCorp\Bundle\EasyAdminBundle\Router\AdminUrlGenerator;
use Exception;
use Symfony\Component\HttpFoundation\RedirectResponse;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;

class UserCrudController extends AbstractCrudController
{
    private readonly ApproveUserRequest $approveUserRequest;
    private readonly NewPasswordUserRequest $newPasswordUserRequest;
    private UserPasswordHasherInterface $passwordEncoder;

    public function __construct(
        UserPasswordHasherInterface $passwordEncoder,
        ApproveUserRequest $approveUserRequest,
        NewPasswordUserRequest $newPasswordUserRequest
    )
    {
        $this->passwordEncoder = $passwordEncoder;
        $this->approveUserRequest = $approveUserRequest;
        $this->newPasswordUserRequest = $newPasswordUserRequest;
    }

    public function configureAssets(Assets $assets): Assets
    {
        return parent::configureAssets($assets)
            ->addJsFile("assets/js/userCrud.js");
    }

    public static function getEntityFqcn(): string
    {
        return User::class;
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
        $actions
            ->add(Crud::PAGE_INDEX, Action::DETAIL);
        $actions
            ->add(Crud::PAGE_INDEX, Action::new('approveRequest', 'Одобрить')
            ->linkToCrudAction('approveRequest'));
        $actions
            ->add(Crud::PAGE_INDEX, Action::new('newPasswordRequest', 'Новый пароль')
            ->linkToCrudAction('newPasswordRequest'));

        $actions->reorder(Crud::PAGE_INDEX, ['approveRequest', 'newPasswordRequest', Action::DETAIL, Action::EDIT, Action::DELETE]);

        return parent::configureActions($actions)
            ->setPermissions(
                [
                    Action::NEW => 'ROLE_ADMIN',
                    Action::DELETE => 'ROLE_ADMIN',
                    Action::EDIT => 'ROLE_ADMIN',
                ]);
    }

    public function approveRequest(EntityManagerInterface $entityManager, AdminUrlGenerator $adminUrlGenerator): RedirectResponse
    {
        $id = $this->getContext()->getRequest()->get('entityId');
        $user = $entityManager->getRepository(User::class)->find($id);

        $currentPage = $this
            ->redirect($adminUrlGenerator
            ->setController(UserCrudController::class)
            ->setAction(Crud::PAGE_INDEX)
            ->generateUrl());

        if (!$user) {
            $this->addFlash('warning', 'Пользователь не найден.');
            return $currentPage;
        }

        if (in_array('ROLE_ADMIN', $user->getRoles())) {
            $this->addFlash('warning', 'Администратора нельзя одобрить');
            return $currentPage;
        }

        if ($user->getIsApproved()) {
            $this->addFlash('warning', 'Пользователь уже одобрен.');
            return $currentPage;
        }

        try {
            // Получаем сгенерированный пароль
            $randomPassword = $this->approveUserRequest->approveUser($entityManager, $user);

            // TODO: отправить пароль пользователю по почте

            $this->addFlash('success', "Пользователь успешно одобрен! Новый пароль: $randomPassword");
        } catch (Exception $e) {
            $this->addFlash('danger', 'Ошибка: ' . $e->getMessage());
        }

        return $currentPage;
    }

    public function newPasswordRequest(EntityManagerInterface $entityManager, AdminUrlGenerator $adminUrlGenerator): RedirectResponse
    {
        $id = $this->getContext()->getRequest()->get('entityId');
        $user = $entityManager->getRepository(User::class)->find($id);

        $currentPage = $this
            ->redirect($adminUrlGenerator
            ->setController(UserCrudController::class)
            ->setAction(Crud::PAGE_INDEX)
            ->generateUrl());

        if (!$user) {
            $this->addFlash('warning', 'Пользователь не найден.');
            return $currentPage;
        }

        if (in_array('ROLE_ADMIN', $user->getRoles())) {
            $this->addFlash('warning', 'Администратора нельзя обновить');
            return $currentPage;
        }

        try {
            // Получаем сгенерированный пароль
            $randomPassword = $this->newPasswordUserRequest->newPasswordRequest($entityManager, $user);

            // TODO: отправить пароль пользователю по почте

            $this->addFlash('success', "Новый пароль: $randomPassword");
        } catch (Exception $e) {
            $this->addFlash('danger', 'Ошибка: ' . $e->getMessage());
        }

        return $currentPage;
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

        yield EmailField::new('email', 'Эл. почта')
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

        yield TextField::new('username', 'Логин')
            ->setColumns(4)
            ->setRequired(true);

        yield TextField::new('contract', 'Договор')
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

        yield AssociationField::new('cars', 'Авто')
            ->setColumns(4)
            ->onlyOnForms();

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

        yield BooleanField::new('is_active', 'Активный?')
            ->setColumns(12)
            ->renderAsSwitch();

        yield BooleanField::new('is_approved', 'Одобрен?')
            ->setColumns(12)
            ->renderAsSwitch()
            ->addCssClass('.approved-switch');

        yield TextEditorField::new('message', 'Сообщение')
            ->setColumns(12)
            ->hideOnIndex()
            ->onlyOnDetail();

        yield TextField::new('password', 'Пароль')
            ->onlyOnDetail();

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

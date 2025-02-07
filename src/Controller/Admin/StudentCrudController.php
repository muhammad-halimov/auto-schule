<?php

namespace App\Controller\Admin;

use App\Entity\Student;
use Doctrine\ORM\EntityManagerInterface;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\AssociationField;
use EasyCorp\Bundle\EasyAdminBundle\Field\BooleanField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\EmailField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;

class StudentCrudController extends AbstractCrudController
{
    private UserPasswordHasherInterface $passwordEncoder;

    public function __construct(UserPasswordHasherInterface $passwordEncoder)
    {
        $this->passwordEncoder = $passwordEncoder;
    }

    public static function getEntityFqcn(): string
    {
        return Student::class;
    }

    public function configureCrud(Crud $crud): Crud
    {
        return parent::configureCrud($crud)
            ->setEntityPermission('ROLE_ADMIN')
            ->setEntityLabelInPlural('Студенты')
            ->setEntityLabelInSingular('студента')
            ->setPageTitle(Crud::PAGE_NEW, 'Добавление студента')
            ->setPageTitle(Crud::PAGE_EDIT, 'Изменение студента')
            ->setPageTitle(Crud::PAGE_DETAIL, "Информация о студенте");
    }

    public function persistEntity(EntityManagerInterface $entityManager, $entityInstance): void
    {
        if ($entityInstance instanceof Student && $entityInstance->getPlainPassword()) {
            $this->addFlash('notice', 'Пароль изменен и сохранен!');
            $entityInstance->setPassword($this->passwordEncoder->hashPassword($entityInstance, $entityInstance->getPlainPassword()));
        }

        parent::persistEntity($entityManager, $entityInstance);
    }

    public function updateEntity(EntityManagerInterface $entityManager, $entityInstance): void
    {
        if ($entityInstance instanceof Student && $entityInstance->getPlainPassword()) {
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
            ->setColumns(4);

        yield TextField::new('contract', 'Номер договора')
            ->setColumns(4)
            ->setRequired(true);

        yield AssociationField::new('course', 'Курс')
            ->setColumns(4);

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

        yield BooleanField::new('examStatus', 'Статус экзамена')
            ->setColumns(9);

        yield DateTimeField::new('dateOfBirth', 'Дата рождения')
            ->setColumns(9)
            ->setRequired(true);

        yield DateTimeField::new('updatedAt', 'Обновлено')
            ->onlyOnIndex();

        yield DateTimeField::new('createdAt', 'Создано')
            ->onlyOnIndex();
    }
}

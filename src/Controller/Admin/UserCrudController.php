<?php /** @noinspection PhpPropertyOnlyWrittenInspection */

namespace App\Controller\Admin;

use App\Controller\Admin\Field\VichImageField;
use App\Entity\User;
use App\Service\ApproveAdminService;
use App\Service\ApproveInstructorService;
use App\Service\ApproveStudentService;
use App\Service\ApproveTeacherService;
use App\Service\AccountConfirmationService;
use Doctrine\ORM\EntityManagerInterface;
use Doctrine\ORM\QueryBuilder;
use EasyCorp\Bundle\EasyAdminBundle\Config\Action;
use EasyCorp\Bundle\EasyAdminBundle\Config\Actions;
use EasyCorp\Bundle\EasyAdminBundle\Config\Assets;
use EasyCorp\Bundle\EasyAdminBundle\Config\Crud;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractCrudController;
use EasyCorp\Bundle\EasyAdminBundle\Field\AssociationField;
use EasyCorp\Bundle\EasyAdminBundle\Field\BooleanField;
use EasyCorp\Bundle\EasyAdminBundle\Field\ChoiceField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateField;
use EasyCorp\Bundle\EasyAdminBundle\Field\DateTimeField;
use EasyCorp\Bundle\EasyAdminBundle\Field\EmailField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IdField;
use EasyCorp\Bundle\EasyAdminBundle\Field\IntegerField;
use EasyCorp\Bundle\EasyAdminBundle\Field\NumberField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TelephoneField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextEditorField;
use EasyCorp\Bundle\EasyAdminBundle\Field\TextField;
use EasyCorp\Bundle\EasyAdminBundle\Router\AdminUrlGenerator;
use Exception;
use Symfony\Component\Form\Extension\Core\Type\TelType;
use Symfony\Component\HttpFoundation\RedirectResponse;
use Symfony\Component\Mailer\Exception\TransportExceptionInterface;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;

class UserCrudController extends AbstractCrudController
{
    private readonly ApproveStudentService $approveUserRequest;
    private readonly ApproveAdminService $approveAdminRequest;
    private readonly ApproveInstructorService $approveInstructorRequest;
    private readonly ApproveTeacherService $approveTeacherRequest;
    private readonly AccountConfirmationService $newPasswordUserRequest;
    private UserPasswordHasherInterface $passwordEncoder;

    public function __construct(
        UserPasswordHasherInterface $passwordEncoder,
        ApproveAdminService         $approveAdminRequest,
        ApproveStudentService       $approveUserRequest,
        ApproveInstructorService    $approveInstructorRequest,
        ApproveTeacherService       $approveTeacherRequest,
        AccountConfirmationService  $newPasswordUserRequest
    )
    {
        $this->passwordEncoder = $passwordEncoder;
        $this->approveUserRequest = $approveUserRequest;
        $this->approveAdminRequest = $approveAdminRequest;
        $this->approveInstructorRequest = $approveInstructorRequest;
        $this->approveTeacherRequest = $approveTeacherRequest;
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
            ->add(Crud::PAGE_INDEX, Action::new('approveRequest', 'Одобрить пользователя')
            ->linkToCrudAction('approveRequest'));

        $actions
            ->add(Crud::PAGE_INDEX, Action::new('confirmPasswordRequest', 'Отправить пароль на почту')
            ->linkToCrudAction('confirmPasswordRequest'));

        $actions
            ->reorder(Crud::PAGE_INDEX, [
                'approveRequest',
                'confirmPasswordRequest',
                Action::DETAIL,
                Action::EDIT,
                Action::DELETE
            ]);

        return parent::configureActions($actions)
            ->setPermissions([
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

        if ($user->getIsApproved()) {
            $this->addFlash('warning', 'Пользователь уже одобрен.');
            return $currentPage;
        }

        if (in_array('ROLE_ADMIN', $user->getRoles())) {
            try {
                $this->approveAdminRequest->approveAdmin($entityManager, $user);
                $this->addFlash('success', "Админ успешно одобрен!");
                return $currentPage;
            } catch (Exception $e) {
                $this->addFlash('danger', 'Ошибка: ' . $e->getMessage());
            }
        }

        if (in_array('ROLE_INSTRUCTOR', $user->getRoles())) {
            try {
                $this->approveInstructorRequest->approveInstructor($entityManager, $user);
                $this->addFlash('success', "Инструктор успешно одобрен!");
                return $currentPage;
            } catch (Exception $e) {
                $this->addFlash('danger', 'Ошибка: ' . $e->getMessage());
            }
        }

        if (in_array('ROLE_TEACHER', $user->getRoles())) {
            try {
                $this->approveTeacherRequest->approveTeacher($entityManager, $user);
                $this->addFlash('success', "Преподаватель успешно одобрен!");
                return $currentPage;
            } catch (Exception $e) {
                $this->addFlash('danger', 'Ошибка: ' . $e->getMessage());
            }
        }

        try {
            $this->approveUserRequest->approveStudent($entityManager, $user);
            $this->addFlash('success', "Студент успешно одобрен!");
        } catch (Exception $e) {
            $this->addFlash('danger', 'Ошибка: ' . $e->getMessage());
        }

        return $currentPage;
    }

    /**
     * @throws TransportExceptionInterface
     */
    public function confirmPasswordRequest(EntityManagerInterface $entityManager, AdminUrlGenerator $adminUrlGenerator): RedirectResponse
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

        if (!$user->getIsActive() && !$user->getIsApproved()) {
            $this->addFlash('warning', 'Пользователь не одобрен, нужно сначала одобрить.');
            return $currentPage;
        }

        try {
            $response = $this->newPasswordUserRequest->sendConfirmationEmail($user);
            $this->addFlash('success', $response);
        } catch (Exception $e) {
            $this->addFlash('danger', "Ошибка: {$e->getMessage()}");
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
            ->addCssClass("form-switch")
            ->setChoices(User::ROLES)
            ->setColumns(9);

        yield BooleanField::new('examStatus', 'Экзамен сдан?')
            ->setColumns(9)
            ->onlyOnForms()
            ->renderAsSwitch()
            ->addCssClass("form-switch");

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

        yield TelephoneField::new('phone', 'Телефон')
            ->setFormType(TelType::class)
            ->addCssClass('field-telephone')
            ->setColumns(4)
            ->setRequired(true);

        yield IntegerField::new('experience', 'Водительский стаж')
            ->setColumns(4)
            ->hideOnIndex();

        yield TextField::new('telegramId', 'Телеграм ID')
            ->setColumns(4);

        yield AssociationField::new('category', 'Категория')
            ->setQueryBuilder(function (QueryBuilder $qb) {
                return $qb
                    ->andWhere("entity.type LIKE :type")
                    ->setParameter('type', 'course');
            })
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

        $plainPassword = TextField::new('plainPassword')
            ->setRequired(false)
            ->onlyOnForms();

        if (crud::PAGE_NEW === $pageName) {
            $plainPassword->setLabel('Пароль')
                ->setRequired(true)
                ->setColumns(4);
        } else {
            $plainPassword->setLabel('Новый пароль')
                ->setColumns(4);
        }

        yield $plainPassword;

        yield AssociationField::new('car', 'Автомобиль')
            ->onlyOnForms()
            ->addCssClass('field-car')
            ->setColumns(4);

        yield NumberField::new('balance', 'Баланс')
            ->hideOnIndex()
            ->setColumns(4);

        yield DateField::new('hireDate', 'Наймам')
            ->setColumns(1)
            ->onlyOnForms()
            ->setRequired(true);

        yield DateField::new('dateOfBirth', 'Рождение')
            ->setColumns(1)
            ->onlyOnForms()
            ->setRequired(true);

        yield DateField::new('enrollDate', 'Поступление')
            ->setColumns(2)
            ->onlyOnForms()
            ->setRequired(true);

        yield TextEditorField::new('aboutMe', 'Обо мне')
            ->setColumns(12)
            ->hideOnIndex();

        yield BooleanField::new('is_active', 'Активный?')
            ->setColumns(12)
            ->renderAsSwitch()
            ->addCssClass("form-switch");

        yield BooleanField::new('is_approved', 'Одобрен?')
            ->setColumns(12)
            ->renderAsSwitch()
            ->addCssClass("form-switch");

        yield VichImageField::new('imageFile', 'Фото профиля')
            ->setHelp('
                <div class="mt-3">
                    <span class="badge badge-info">*.jpg</span>
                    <span class="badge badge-info">*.jpeg</span>
                    <span class="badge badge-info">*.png</span>
                    <span class="badge badge-info">*.jiff</span>
                    <span class="badge badge-info">*.webp</span>
                </div>
            ')
            ->onlyOnForms()
            ->setColumns(4);

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

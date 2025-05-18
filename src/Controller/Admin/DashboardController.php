<?php

namespace App\Controller\Admin;

use App\Entity\Autodrome;
use App\Entity\AutoProducer;
use App\Entity\Car;
use App\Entity\Category;
use App\Entity\Course;
use App\Entity\CourseQuiz;
use App\Entity\CourseQuizAnswers;
use App\Entity\DriveSchedule;
use App\Entity\Exam;
use App\Entity\InstructorLesson;
use App\Entity\Price;
use App\Entity\Review;
use App\Entity\TeacherLesson;
use App\Entity\User;
use EasyCorp\Bundle\EasyAdminBundle\Config\Dashboard;
use EasyCorp\Bundle\EasyAdminBundle\Config\MenuItem;
use EasyCorp\Bundle\EasyAdminBundle\Controller\AbstractDashboardController;
use EasyCorp\Bundle\EasyAdminBundle\Router\AdminUrlGenerator;
use Psr\Container\ContainerExceptionInterface;
use Psr\Container\NotFoundExceptionInterface;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class DashboardController extends AbstractDashboardController
{
    /**
     * @throws NotFoundExceptionInterface
     * @throws ContainerExceptionInterface
     * @IsGranted("ROLE_ADMIN")
     * @IsGranted("ROLE_TEACHER")
     * @IsGranted("ROLE_INSTRUCTOR")
     */
    #[Route(path: '/admin', name: 'admin')]
    public function index(): Response
    {
        return $this
            ->redirect(url: $this->container
            ->get(AdminUrlGenerator::class)
            ->setController(CourseCrudController::class)
            ->generateUrl());
    }

    public function configureDashboard(): Dashboard
    {
        return Dashboard::new()
            ->setTitle('Автошкола Endeavor')
            ->setFaviconPath('favicon.ico')
            ->renderContentMaximized();
    }

    public function __construct(){}

    public function configureMenuItems(): iterable
    {
        yield MenuItem::section('Теория');
            yield MenuItem::linkToCrud('Курсы', 'fa fa-graduation-cap', Course::class);
            yield MenuItem::linkToCrud('Занятия', 'fa fa-book', TeacherLesson::class);
            yield MenuItem::linkToCrud('Тесты', 'fa fa-circle-question', CourseQuiz::class);

        yield MenuItem::section('Практика');
            yield MenuItem::linkToCrud('Цены', 'fa fa-sack-dollar', Price::class);
            yield MenuItem::linkToCrud('Вождение', 'fa fa-car', InstructorLesson::class);
            yield MenuItem::linkToCrud('Экзамены', 'fa fa-ticket', Exam::class);
            yield MenuItem::linkToCrud('Расписание', 'fa fa-calendar', DriveSchedule::class);

        yield MenuItem::section('Настройки');
            yield MenuItem::linkToCrud('Категории', 'fa fa-layer-group', Category::class);
            yield MenuItem::linkToCrud('Автодромы', 'fa fa-square-parking', Autodrome::class);
            yield MenuItem::linkToCrud('Автомобили', 'fa fa-car-side', Car::class);
            yield MenuItem::linkToCrud('Автопроизводители', 'fa fa-link', AutoProducer::class);

        yield MenuItem::section('Пользователи');
            yield MenuItem::linkToCrud('Пользователи', 'fa fa-users', User::class);
            yield MenuItem::linkToCrud('Отзывы', 'fa fa-at', Review::class);

        yield MenuItem::section('Доп. настройки');
            yield MenuItem::linkToUrl('API', 'fa fa-link', '/api')
                ->setLinkTarget('_blank')
                ->setPermission('ROLE_ADMIN');
    }
}
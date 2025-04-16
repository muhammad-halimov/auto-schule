<?php

namespace App\Controller;

use App\Entity\User;
use App\Repository\UserRepository;
use Doctrine\ORM\EntityManagerInterface;
use LogicException;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\Security\Http\Authentication\AuthenticationUtils;

class SecurityController extends AbstractController
{
    #[Route(path: '/admin/login', name: 'app_login')]
    public function login(AuthenticationUtils    $authenticationUtils,
                          UserRepository         $repository,
                          EntityManagerInterface $entityManager): Response
    {
        if ($this->getUser()) {
            return $this->redirectToRoute('admin');
        }

        $userAdmin = $repository->findOneBy(['email' => 'admin@admin.com']);
        if (!$userAdmin) {
            $userAdmin = (new User())
                ->setEmail('admin@admin.com')
                ->setUsername('admin')
                ->setRoles(['ROLE_ADMIN'])
                ->setPassword('$2y$13$dKHroammGwy5m..V51QWzeoMwdltwX.sn2kU.xwa1Z52wrZ4qAqya');
            $entityManager->persist($userAdmin);
            $entityManager->flush();
        }

        // get the login error if there is one
        $error = $authenticationUtils->getLastAuthenticationError();
        // last username entered by the user
        $lastUsername = $authenticationUtils->getLastUsername();

        return $this->render('@EasyAdmin/page/login.html.twig', [
            // parameters usually defined in Symfony login forms
            'error' => $error,
            'last_username' => $lastUsername,

            // OPTIONAL parameters to customize the login form:

            // the translation_domain to use (define this option only if you are
            // rendering the login template in a regular Symfony controller; when
            // rendering it from an EasyAdmin Dashboard this is automatically set to
            // the same domain as the rest of the Dashboard)
            'translation_domain' => 'admin',

            // the title visible above the login form (define this option only if you are
            // rendering the login template in a regular Symfony controller; when rendering
            // it from an EasyAdmin Dashboard this is automatically set as the Dashboard title)
            // 'page_title' => 'ACME login',

            // the string used to generate the CSRF token. If you don't define
            // this parameter, the login form won't include a CSRF token
            'csrf_token_intention' => 'authenticate',

            // the URL users are redirected to after the login (default: '/admin')
            'target_path' => $this->generateUrl('admin'),

            // the label displayed for the username form field (the |trans filter is applied to it)
            'username_label' => 'Почта',

            // the label displayed for the password form field (the |trans filter is applied to it)
            'password_label' => 'Пароль',

            // the label displayed for the Sign-In form button (the |trans filter is applied to it)
            'sign_in_label' => 'Вход',

            // the 'name' HTML attribute of the <input> used for the username field (default: '_username')
            // 'username_parameter' => 'my_custom_username_field',

            // the 'name' HTML attribute of the <input> used for the password field (default: '_password')
            // 'password_parameter' => 'my_custom_password_field',

            // whether to enable or not the "forgot password?" link (default: false)
            'forgot_password_enabled' => false,

            // the path (i.e. a relative or absolute URL) to visit when clicking the "forgot password?" link (default: '#')
            'forgot_password_path' => '#',//$this->generateUrl('app_how_reset'),

            // the label displayed for the "forgot password?" link (the |trans filter is applied to it)
            'forgot_password_label' => 'Забыли пароль?',

            // whether to enable or not the "remember me" checkbox (default: false)
            'remember_me_enabled' => true,

            // remember me name form field (default: '_remember_me')
            'remember_me_parameter' => 'custom_remember_me_param',

            // whether to check by default the "remember me" checkbox (default: false)
            'remember_me_checked' => true,

            // the label displayed for the remember me checkbox (the |trans filter is applied to it)
            'remember_me_label' => 'Запомнить',
        ]);
    }

    #[Route(path: '/admin/logout', name: 'app_logout')]
    public function logout(): void
    {
        throw new LogicException('This method can be blank - it will be intercepted by the logout key on your firewall.');
    }
}

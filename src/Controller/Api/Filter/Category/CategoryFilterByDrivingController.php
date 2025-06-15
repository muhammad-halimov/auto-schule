<?php


namespace App\Controller\Api\Filter\Category;

use App\Repository\CategoryRepository;
use Exception;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;

class CategoryFilterByDrivingController extends AbstractController
{
    private readonly CategoryRepository $categoryRepository;

    public function __construct(CategoryRepository $categoryRepository)
    {
        $this->categoryRepository = $categoryRepository;
    }

    public function __invoke(): JsonResponse
    {
        try {
            $categories = $this->categoryRepository->findCategoryByDrivingType();

            return empty($categories)
                ? $this->json([])
                : $this->json($categories, 200, [], ['groups' => ['category:read']]);
        }
        catch (Exception $e) {
            return $this->json([
                'error' => $e->getMessage(),
                'trace' => $e->getTrace()
            ], 500);
        }
    }

}

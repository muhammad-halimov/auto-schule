<?php

namespace App\OpenApi;

use ApiPlatform\OpenApi\Factory\OpenApiFactoryInterface;
use ApiPlatform\OpenApi\OpenApi;

readonly class JwtDecorator implements OpenApiFactoryInterface
{
    public function __construct(private OpenApiFactoryInterface $decorated){}

    public function __invoke(array $context = []): OpenApi
    {
        return $this->decorated->__invoke($context);
    }
}

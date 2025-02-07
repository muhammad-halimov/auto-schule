<?php

namespace App\OpenApi;

use ApiPlatform\OpenApi\Factory\OpenApiFactoryInterface;
use ApiPlatform\OpenApi\Model;
use ApiPlatform\OpenApi\OpenApi;
use ArrayObject;

readonly class JwtClientDecorator implements OpenApiFactoryInterface
{
    public function __construct(private OpenApiFactoryInterface $decorated) {}

    public function __invoke(array $context = []): OpenApi
    {
        $openApi = $this->decorated->__invoke($context);
        $schemas = $openApi->getComponents()->getSchemas();

        $schemas['Client'] = new ArrayObject([
            'type' => 'object',
            'properties' => [
                'token' => [
                    'type' => 'string',
                    'readOnly' => true,
                ],
            ],
        ]);
        $schemas['CredentialsClient'] = new ArrayObject([
            'type' => 'object',
            'properties' => [
                'username' => [
                    'type' => 'string',
                    'example' => 'username',
                ],
                'password' => [
                    'type' => 'string',
                    'example' => 'password',
                ],
            ],
        ]);

        $pathUserAuthentication = new Model\PathItem(
            ref: 'JWT Token',
            post: new Model\Operation(
                operationId: 'postCredentialsItem',
                tags: ['Client'],
                responses: [
                    '200' => [
                        'description' => 'Get Client JWT token',
                        'content' => [
                            'application/json' => [
                                'schema' => [
                                    '$ref' => '#/components/schemas/Client',
                                ],
                            ],
                        ],
                    ],
                ],
                summary: 'Get Client JWT token to login.',
                requestBody: new Model\RequestBody(
                    description: 'Generate Client new JWT Token',
                    content: new ArrayObject([
                        'application/json' => [
                            'schema' => [
                                '$ref' => '#/components/schemas/CredentialsClient',
                            ],
                        ],
                    ]),
                ),
                security: [],
            ),
        );

        $openApi->getPaths()->addPath('/api/authentication_token', $pathUserAuthentication);

        return $openApi;
    }
}

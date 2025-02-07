<?php


namespace App\OpenApi;

use ApiPlatform\OpenApi\Factory\OpenApiFactoryInterface;
use ApiPlatform\OpenApi\Model;
use ApiPlatform\OpenApi\OpenApi;
use ArrayObject;

readonly class JwtTeacherDecorator implements OpenApiFactoryInterface
{
    public function __construct(private OpenApiFactoryInterface $decorated){}

    public function __invoke(array $context = []): OpenApi
    {
        $openApi = $this->decorated->__invoke($context);
        $schemas = $openApi->getComponents()->getSchemas();

        $schemas['Teacher'] = new ArrayObject([
            'type' => 'object',
            'properties' => [
                'token' => [
                    'type' => 'string',
                    'readOnly' => true,
                ],
            ],
        ]);
        $schemas['CredentialsTeacher'] = new ArrayObject([
            'type' => 'object',
            'properties' => [
                'email' => [
                    'type' => 'string',
                    'example' => 'email',
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
                tags: ['Teacher'],
                responses: [
                    '200' => [
                        'description' => 'Get Teacher JWT token',
                        'content' => [
                            'application/json' => [
                                'schema' => [
                                    '$ref' => '#/components/schemas/Teacher',
                                ],
                            ],
                        ],
                    ],
                ],
                summary: 'Get Teacher JWT token to login.',
                requestBody: new Model\RequestBody(
                    description: 'Generate Teacher new JWT Token',
                    content: new ArrayObject([
                        'application/json' => [
                            'schema' => [
                                '$ref' => '#/components/schemas/CredentialsTeacher',
                            ],
                        ],
                    ]),
                ),
                security: [],
            ),
        );

        $openApi->getPaths()->addPath('/api/authentication_token_teacher', $pathUserAuthentication);

        return $openApi;
    }
}

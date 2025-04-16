<?php

namespace App\Controller\Admin\Field;

use EasyCorp\Bundle\EasyAdminBundle\Config\Asset;
use EasyCorp\Bundle\EasyAdminBundle\Contracts\Field\FieldInterface;
use EasyCorp\Bundle\EasyAdminBundle\Field\FieldTrait;
use Vich\UploaderBundle\Form\Type\VichFileType;

class VichVideoField implements FieldInterface
{
    use FieldTrait;

    public static function new(string $propertyName, ?string $label = null)
    {
        return (new self())
            ->setProperty($propertyName)
            ->setLabel($label)
            // this template is used in 'index' and 'detail' pages
            ->setTemplatePath('admin/field/vich_video.html.twig')
            ->addCssClass('field-image')
            ->addJsFiles(Asset::fromEasyAdminAssetPackage('field-image.js'), Asset::fromEasyAdminAssetPackage('field-file-upload.js'))
            ->setFormType(VichFileType::class)
            ->addCssClass('field-vich-image');
    }
}

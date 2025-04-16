<?php

namespace App\Controller\Admin\Field;

use EasyCorp\Bundle\EasyAdminBundle\Contracts\Field\FieldInterface;
use EasyCorp\Bundle\EasyAdminBundle\Field\FieldTrait;
use Vich\UploaderBundle\Form\Type\VichImageType;

class VichGalleryField implements FieldInterface
{
    use FieldTrait;

    public static function new(string $propertyName, ?string $label = null): VichGalleryField
    {
        return (new self())
            ->setProperty($propertyName)
            ->setLabel($label)
            ->setTemplatePath('admin/field/vich_gallery.html.twig')
            ->addCssFiles('/vich/vich_gallery.css')
            ->addJsFiles('/vich/vich_gallery.js')
            ->setFormType(VichImageType::class)
            ->addCssClass('field-vich-image');
    }
}
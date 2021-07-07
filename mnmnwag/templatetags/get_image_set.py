from django import template

register = template.Library()


@register.filter
def get_image_set(slides):
    """
    Generate a comma-separated list of image IDs given a list of
    slides from a SlidesBlock.
    """
    img_set = [img['image'].id for img in slides]
    img_set = ','.join(map(str, img_set))
    return img_set

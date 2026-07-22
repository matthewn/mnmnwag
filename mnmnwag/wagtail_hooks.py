from django.templatetags.static import static
from django.utils.html import format_html
from taggit.models import Tag
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
import wagtail.admin.rich_text.editors.draftail.features as draftail_features


@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static('css/admin.css'),
    )


@hooks.register('register_admin_menu_item')
def register_add_subpage_menu_item():
    return MenuItem(
        'New blog post',
        '/cms/pages/4/add_subpage/',
        name='new-blogpost',
        icon_name='plus',
        order=1,
    )


@hooks.register('register_rich_text_features')
def register_kbd_feature(features):
    """
    provides <kbd></kbd>
    indebted to https://timlwhite.medium.com/custom-in-line-styles-with-draftail-939201c2bbda
    """
    feature_name = 'kbd'
    type_ = 'KBD'
    control = {
        'type': type_,
        'label': 'K',
        'description': 'Kbd',
        'style': {
            'background-color': 'rgba(27, 31, 35, 0.05)',
            'font-family': 'Consolas, Menlo, Monaco, Lucida Console, Liberation Mono, DejaVu Sans Mono, Bitstream Vera Sans Mono, Courier New, monospace, sans-serif',
            'font-size': '85%',
            'margin': '0px',
            'padding': '0.2em 0.3125em',
        }
    }
    features.register_editor_plugin(
        'draftail',
        feature_name,
        draftail_features.InlineStyleFeature(control)
    )
    db_conversion = {
        'from_database_format': {
            'kbd': InlineStyleElementHandler(type_)
        },
        'to_database_format': {
            'style_map': {type_: 'kbd'}
        },
    }
    features.register_converter_rule(
        'contentstate',
        feature_name,
        db_conversion
    )


class TagViewSet(SnippetViewSet):
    model = Tag
    icon = 'tag'
    list_display = ['name', 'slug']
    list_per_page = 1000
    ordering = ['name']


register_snippet(TagViewSet)

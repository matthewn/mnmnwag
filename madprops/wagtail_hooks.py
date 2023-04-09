from wagtail import hooks
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler
import wagtail.admin.rich_text.editors.draftail.features as draftail_features


@hooks.register('register_rich_text_features')
def register_yes_feature(features):
    """
    provides <span class="yes"></span>
    indebted to https://timlwhite.medium.com/custom-in-line-styles-with-draftail-939201c2bbda
    """
    feature_name = 'yes'
    type_ = 'YES'
    control = {
        'type': type_,
        'label': 'Y',
        'description': 'YES',
        'style': {
            'font-weight': 'bold',
        }
    }
    features.register_editor_plugin(
        'draftail',
        feature_name,
        draftail_features.InlineStyleFeature(control)
    )
    db_conversion = {
        'from_database_format': {
            'span[class="yes"]': InlineStyleElementHandler(type_)
        },
        'to_database_format': {
            'style_map': {type_: 'span class="yes"'}
        },
    }
    features.register_converter_rule(
        'contentstate',
        feature_name,
        db_conversion
    )


@hooks.register('register_rich_text_features')
def register_no_feature(features):
    """
    provides <span class="no"></span>
    indebted to https://timlwhite.medium.com/custom-in-line-styles-with-draftail-939201c2bbda
    """
    feature_name = 'no'
    type_ = 'NO'
    control = {
        'type': type_,
        'label': 'N',
        'description': 'NO',
        'style': {
            'font-weight': 'bold',
        }
    }
    features.register_editor_plugin(
        'draftail',
        feature_name,
        draftail_features.InlineStyleFeature(control)
    )
    db_conversion = {
        'from_database_format': {
            'span[class="no"]': InlineStyleElementHandler(type_)
        },
        'to_database_format': {
            'style_map': {type_: 'span class="no"'}
        },
    }
    features.register_converter_rule(
        'contentstate',
        feature_name,
        db_conversion
    )

# Generated by Django 4.1.7 on 2023-04-22 20:21

from django.db import migrations, models
import mnmnwag.blocks
import wagtail.blocks
import wagtail.blocks.field_block
import wagtail.embeds.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ("madprops", "0004_simplepage"),
    ]

    operations = [
        migrations.AddField(
            model_name="editionpage",
            name="has_comments_enabled",
            field=models.BooleanField(default=True, verbose_name="Comments enabled"),
        ),
        migrations.AlterField(
            model_name="archivespage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    ("heading", wagtail.blocks.CharBlock(form_classname="full title")),
                    (
                        "paragraph",
                        wagtail.blocks.RichTextBlock(
                            features=[
                                "h3",
                                "h4",
                                "h5",
                                "ol",
                                "ul",
                                "blockquote",
                                "yes",
                                "no",
                                "bold",
                                "italic",
                                "superscript",
                                "subscript",
                                "strikethrough",
                                "code",
                                "link",
                                "image",
                                "document-link",
                            ]
                        ),
                    ),
                    (
                        "image",
                        wagtail.blocks.StructBlock(
                            [
                                ("image", wagtail.images.blocks.ImageChooserBlock()),
                                (
                                    "caption",
                                    wagtail.blocks.RichTextBlock(
                                        features=["bold", "italic", "link"],
                                        required=False,
                                    ),
                                ),
                                (
                                    "alt_text",
                                    wagtail.blocks.CharBlock(
                                        max_length=256, required=False
                                    ),
                                ),
                                ("link", wagtail.blocks.URLBlock(required=False)),
                                (
                                    "float",
                                    wagtail.blocks.ChoiceBlock(
                                        blank=False,
                                        choices=[
                                            (3, "None"),
                                            (1, "Left"),
                                            (2, "Right"),
                                        ],
                                    ),
                                ),
                                (
                                    "zoom",
                                    wagtail.blocks.ChoiceBlock(
                                        choices=[(0, "Off"), (1, "On")]
                                    ),
                                ),
                            ]
                        ),
                    ),
                    ("embed", wagtail.embeds.blocks.EmbedBlock()),
                    ("media", mnmnwag.blocks.MediaBlock(icon="media")),
                    ("raw_HTML", wagtail.blocks.RawHTMLBlock(required=False)),
                    (
                        "danger",
                        wagtail.blocks.RawHTMLBlock(label="DANGER!", required=False),
                    ),
                    (
                        "prop",
                        wagtail.blocks.StructBlock(
                            [
                                ("prop_number", wagtail.blocks.IntegerBlock()),
                                ("prop_title", wagtail.blocks.CharBlock()),
                                (
                                    "info_links",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.field_block.URLBlock
                                    ),
                                ),
                                (
                                    "recommendation",
                                    wagtail.blocks.ChoiceBlock(
                                        choices=[
                                            ("yes", "Yes"),
                                            ("no", "No"),
                                            ("nopos", "No position"),
                                            ("noadv", "No position (advisory measure)"),
                                        ]
                                    ),
                                ),
                                (
                                    "writeup",
                                    wagtail.blocks.StreamBlock(
                                        [
                                            (
                                                "heading",
                                                wagtail.blocks.CharBlock(
                                                    form_classname="full title"
                                                ),
                                            ),
                                            (
                                                "paragraph",
                                                wagtail.blocks.RichTextBlock(
                                                    features=[
                                                        "h3",
                                                        "h4",
                                                        "h5",
                                                        "ol",
                                                        "ul",
                                                        "blockquote",
                                                        "yes",
                                                        "no",
                                                        "bold",
                                                        "italic",
                                                        "superscript",
                                                        "subscript",
                                                        "strikethrough",
                                                        "code",
                                                        "link",
                                                        "image",
                                                        "document-link",
                                                    ]
                                                ),
                                            ),
                                            (
                                                "image",
                                                wagtail.blocks.StructBlock(
                                                    [
                                                        (
                                                            "image",
                                                            wagtail.images.blocks.ImageChooserBlock(),
                                                        ),
                                                        (
                                                            "caption",
                                                            wagtail.blocks.RichTextBlock(
                                                                features=[
                                                                    "bold",
                                                                    "italic",
                                                                    "link",
                                                                ],
                                                                required=False,
                                                            ),
                                                        ),
                                                        (
                                                            "alt_text",
                                                            wagtail.blocks.CharBlock(
                                                                max_length=256,
                                                                required=False,
                                                            ),
                                                        ),
                                                        (
                                                            "link",
                                                            wagtail.blocks.URLBlock(
                                                                required=False
                                                            ),
                                                        ),
                                                        (
                                                            "float",
                                                            wagtail.blocks.ChoiceBlock(
                                                                blank=False,
                                                                choices=[
                                                                    (3, "None"),
                                                                    (1, "Left"),
                                                                    (2, "Right"),
                                                                ],
                                                            ),
                                                        ),
                                                        (
                                                            "zoom",
                                                            wagtail.blocks.ChoiceBlock(
                                                                choices=[
                                                                    (0, "Off"),
                                                                    (1, "On"),
                                                                ]
                                                            ),
                                                        ),
                                                    ]
                                                ),
                                            ),
                                            (
                                                "embed",
                                                wagtail.embeds.blocks.EmbedBlock(),
                                            ),
                                            (
                                                "media",
                                                mnmnwag.blocks.MediaBlock(icon="media"),
                                            ),
                                            (
                                                "raw_HTML",
                                                wagtail.blocks.RawHTMLBlock(
                                                    required=False
                                                ),
                                            ),
                                            (
                                                "danger",
                                                wagtail.blocks.RawHTMLBlock(
                                                    label="DANGER!", required=False
                                                ),
                                            ),
                                        ]
                                    ),
                                ),
                            ]
                        ),
                    ),
                ],
                use_json_field=True,
            ),
        ),
        migrations.AlterField(
            model_name="editionpage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    ("heading", wagtail.blocks.CharBlock(form_classname="full title")),
                    (
                        "paragraph",
                        wagtail.blocks.RichTextBlock(
                            features=[
                                "h3",
                                "h4",
                                "h5",
                                "ol",
                                "ul",
                                "blockquote",
                                "yes",
                                "no",
                                "bold",
                                "italic",
                                "superscript",
                                "subscript",
                                "strikethrough",
                                "code",
                                "link",
                                "image",
                                "document-link",
                            ]
                        ),
                    ),
                    (
                        "image",
                        wagtail.blocks.StructBlock(
                            [
                                ("image", wagtail.images.blocks.ImageChooserBlock()),
                                (
                                    "caption",
                                    wagtail.blocks.RichTextBlock(
                                        features=["bold", "italic", "link"],
                                        required=False,
                                    ),
                                ),
                                (
                                    "alt_text",
                                    wagtail.blocks.CharBlock(
                                        max_length=256, required=False
                                    ),
                                ),
                                ("link", wagtail.blocks.URLBlock(required=False)),
                                (
                                    "float",
                                    wagtail.blocks.ChoiceBlock(
                                        blank=False,
                                        choices=[
                                            (3, "None"),
                                            (1, "Left"),
                                            (2, "Right"),
                                        ],
                                    ),
                                ),
                                (
                                    "zoom",
                                    wagtail.blocks.ChoiceBlock(
                                        choices=[(0, "Off"), (1, "On")]
                                    ),
                                ),
                            ]
                        ),
                    ),
                    ("embed", wagtail.embeds.blocks.EmbedBlock()),
                    ("media", mnmnwag.blocks.MediaBlock(icon="media")),
                    ("raw_HTML", wagtail.blocks.RawHTMLBlock(required=False)),
                    (
                        "danger",
                        wagtail.blocks.RawHTMLBlock(label="DANGER!", required=False),
                    ),
                    (
                        "prop",
                        wagtail.blocks.StructBlock(
                            [
                                ("prop_number", wagtail.blocks.IntegerBlock()),
                                ("prop_title", wagtail.blocks.CharBlock()),
                                (
                                    "info_links",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.field_block.URLBlock
                                    ),
                                ),
                                (
                                    "recommendation",
                                    wagtail.blocks.ChoiceBlock(
                                        choices=[
                                            ("yes", "Yes"),
                                            ("no", "No"),
                                            ("nopos", "No position"),
                                            ("noadv", "No position (advisory measure)"),
                                        ]
                                    ),
                                ),
                                (
                                    "writeup",
                                    wagtail.blocks.StreamBlock(
                                        [
                                            (
                                                "heading",
                                                wagtail.blocks.CharBlock(
                                                    form_classname="full title"
                                                ),
                                            ),
                                            (
                                                "paragraph",
                                                wagtail.blocks.RichTextBlock(
                                                    features=[
                                                        "h3",
                                                        "h4",
                                                        "h5",
                                                        "ol",
                                                        "ul",
                                                        "blockquote",
                                                        "yes",
                                                        "no",
                                                        "bold",
                                                        "italic",
                                                        "superscript",
                                                        "subscript",
                                                        "strikethrough",
                                                        "code",
                                                        "link",
                                                        "image",
                                                        "document-link",
                                                    ]
                                                ),
                                            ),
                                            (
                                                "image",
                                                wagtail.blocks.StructBlock(
                                                    [
                                                        (
                                                            "image",
                                                            wagtail.images.blocks.ImageChooserBlock(),
                                                        ),
                                                        (
                                                            "caption",
                                                            wagtail.blocks.RichTextBlock(
                                                                features=[
                                                                    "bold",
                                                                    "italic",
                                                                    "link",
                                                                ],
                                                                required=False,
                                                            ),
                                                        ),
                                                        (
                                                            "alt_text",
                                                            wagtail.blocks.CharBlock(
                                                                max_length=256,
                                                                required=False,
                                                            ),
                                                        ),
                                                        (
                                                            "link",
                                                            wagtail.blocks.URLBlock(
                                                                required=False
                                                            ),
                                                        ),
                                                        (
                                                            "float",
                                                            wagtail.blocks.ChoiceBlock(
                                                                blank=False,
                                                                choices=[
                                                                    (3, "None"),
                                                                    (1, "Left"),
                                                                    (2, "Right"),
                                                                ],
                                                            ),
                                                        ),
                                                        (
                                                            "zoom",
                                                            wagtail.blocks.ChoiceBlock(
                                                                choices=[
                                                                    (0, "Off"),
                                                                    (1, "On"),
                                                                ]
                                                            ),
                                                        ),
                                                    ]
                                                ),
                                            ),
                                            (
                                                "embed",
                                                wagtail.embeds.blocks.EmbedBlock(),
                                            ),
                                            (
                                                "media",
                                                mnmnwag.blocks.MediaBlock(icon="media"),
                                            ),
                                            (
                                                "raw_HTML",
                                                wagtail.blocks.RawHTMLBlock(
                                                    required=False
                                                ),
                                            ),
                                            (
                                                "danger",
                                                wagtail.blocks.RawHTMLBlock(
                                                    label="DANGER!", required=False
                                                ),
                                            ),
                                        ]
                                    ),
                                ),
                            ]
                        ),
                    ),
                ],
                use_json_field=True,
            ),
        ),
        migrations.AlterField(
            model_name="simplepage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    ("heading", wagtail.blocks.CharBlock(form_classname="full title")),
                    (
                        "paragraph",
                        wagtail.blocks.RichTextBlock(
                            features=[
                                "h3",
                                "h4",
                                "h5",
                                "ol",
                                "ul",
                                "blockquote",
                                "yes",
                                "no",
                                "bold",
                                "italic",
                                "superscript",
                                "subscript",
                                "strikethrough",
                                "code",
                                "link",
                                "image",
                                "document-link",
                            ]
                        ),
                    ),
                    (
                        "image",
                        wagtail.blocks.StructBlock(
                            [
                                ("image", wagtail.images.blocks.ImageChooserBlock()),
                                (
                                    "caption",
                                    wagtail.blocks.RichTextBlock(
                                        features=["bold", "italic", "link"],
                                        required=False,
                                    ),
                                ),
                                (
                                    "alt_text",
                                    wagtail.blocks.CharBlock(
                                        max_length=256, required=False
                                    ),
                                ),
                                ("link", wagtail.blocks.URLBlock(required=False)),
                                (
                                    "float",
                                    wagtail.blocks.ChoiceBlock(
                                        blank=False,
                                        choices=[
                                            (3, "None"),
                                            (1, "Left"),
                                            (2, "Right"),
                                        ],
                                    ),
                                ),
                                (
                                    "zoom",
                                    wagtail.blocks.ChoiceBlock(
                                        choices=[(0, "Off"), (1, "On")]
                                    ),
                                ),
                            ]
                        ),
                    ),
                    ("embed", wagtail.embeds.blocks.EmbedBlock()),
                    ("media", mnmnwag.blocks.MediaBlock(icon="media")),
                    ("raw_HTML", wagtail.blocks.RawHTMLBlock(required=False)),
                    (
                        "danger",
                        wagtail.blocks.RawHTMLBlock(label="DANGER!", required=False),
                    ),
                    (
                        "prop",
                        wagtail.blocks.StructBlock(
                            [
                                ("prop_number", wagtail.blocks.IntegerBlock()),
                                ("prop_title", wagtail.blocks.CharBlock()),
                                (
                                    "info_links",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.field_block.URLBlock
                                    ),
                                ),
                                (
                                    "recommendation",
                                    wagtail.blocks.ChoiceBlock(
                                        choices=[
                                            ("yes", "Yes"),
                                            ("no", "No"),
                                            ("nopos", "No position"),
                                            ("noadv", "No position (advisory measure)"),
                                        ]
                                    ),
                                ),
                                (
                                    "writeup",
                                    wagtail.blocks.StreamBlock(
                                        [
                                            (
                                                "heading",
                                                wagtail.blocks.CharBlock(
                                                    form_classname="full title"
                                                ),
                                            ),
                                            (
                                                "paragraph",
                                                wagtail.blocks.RichTextBlock(
                                                    features=[
                                                        "h3",
                                                        "h4",
                                                        "h5",
                                                        "ol",
                                                        "ul",
                                                        "blockquote",
                                                        "yes",
                                                        "no",
                                                        "bold",
                                                        "italic",
                                                        "superscript",
                                                        "subscript",
                                                        "strikethrough",
                                                        "code",
                                                        "link",
                                                        "image",
                                                        "document-link",
                                                    ]
                                                ),
                                            ),
                                            (
                                                "image",
                                                wagtail.blocks.StructBlock(
                                                    [
                                                        (
                                                            "image",
                                                            wagtail.images.blocks.ImageChooserBlock(),
                                                        ),
                                                        (
                                                            "caption",
                                                            wagtail.blocks.RichTextBlock(
                                                                features=[
                                                                    "bold",
                                                                    "italic",
                                                                    "link",
                                                                ],
                                                                required=False,
                                                            ),
                                                        ),
                                                        (
                                                            "alt_text",
                                                            wagtail.blocks.CharBlock(
                                                                max_length=256,
                                                                required=False,
                                                            ),
                                                        ),
                                                        (
                                                            "link",
                                                            wagtail.blocks.URLBlock(
                                                                required=False
                                                            ),
                                                        ),
                                                        (
                                                            "float",
                                                            wagtail.blocks.ChoiceBlock(
                                                                blank=False,
                                                                choices=[
                                                                    (3, "None"),
                                                                    (1, "Left"),
                                                                    (2, "Right"),
                                                                ],
                                                            ),
                                                        ),
                                                        (
                                                            "zoom",
                                                            wagtail.blocks.ChoiceBlock(
                                                                choices=[
                                                                    (0, "Off"),
                                                                    (1, "On"),
                                                                ]
                                                            ),
                                                        ),
                                                    ]
                                                ),
                                            ),
                                            (
                                                "embed",
                                                wagtail.embeds.blocks.EmbedBlock(),
                                            ),
                                            (
                                                "media",
                                                mnmnwag.blocks.MediaBlock(icon="media"),
                                            ),
                                            (
                                                "raw_HTML",
                                                wagtail.blocks.RawHTMLBlock(
                                                    required=False
                                                ),
                                            ),
                                            (
                                                "danger",
                                                wagtail.blocks.RawHTMLBlock(
                                                    label="DANGER!", required=False
                                                ),
                                            ),
                                        ]
                                    ),
                                ),
                            ]
                        ),
                    ),
                ],
                use_json_field=True,
            ),
        ),
    ]

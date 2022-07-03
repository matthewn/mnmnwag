from antispam import akismet
from crequest.middleware import CrequestMiddleware
from django import forms
from django_comments_xtd.forms import XtdCommentForm
from django_comments_xtd.conf import settings


class MahnaCommentForm(XtdCommentForm):
    followup = forms.BooleanField(
        required=False,
        label='Receive email notifications for replies',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'] = forms.CharField(
            label='Name',
            widget=forms.TextInput(
                attrs={
                    'placeholder': 'name (published with your comment)',
                    'class': 'form-control',
                }
            )
        )
        self.fields['email'] = forms.EmailField(
            label='Email',
            widget=forms.TextInput(
                attrs={
                    'placeholder': 'email address (unpublished)',
                    'class': 'form-control',
                }
            )
        )
        self.fields['url'] = forms.URLField(
            label='Link',
            required=False,
            widget=forms.TextInput(
                attrs={
                    'placeholder': 'optional: your name links here',
                    'class': 'form-control',
                }
            )
        )
        self.fields['comment'] = forms.CharField(
            widget=forms.Textarea(
                attrs={
                    'placeholder': 'your comment',
                    'class': 'form-control',
                }
            ),
            max_length=settings.COMMENT_MAX_LENGTH
        )

    def clean_comment(self):
        # run comment through akismet before accepting
        # https://django-antispam.readthedocs.io/en/latest/usage.html#akismet
        request = CrequestMiddleware.get_request()
        if request and akismet.check(
            request=akismet.Request.from_django_request(request),
            comment=akismet.Comment(
                content=self.cleaned_data['comment'],
                type='comment',
                author=akismet.Author(
                    name=self.cleaned_data['name'],
                    email=self.cleaned_data['email']
                )
            )
        ):
            raise forms.ValidationError('Spam detected', code='spam-protection')
        return super().clean_comment()

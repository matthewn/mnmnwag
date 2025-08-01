from django.conf.global_settings import (
    DATETIME_INPUT_FORMATS,
    TIME_INPUT_FORMATS,
)

# for 12-hour clock support in Wagtail admin
DATETIME_INPUT_FORMATS += [
    '%Y-%m-%d %I:%M %p',     # 2006-10-25 02:30 PM
]
TIME_INPUT_FORMATS += [
    '%I:%M %p',     # '02:30 PM'
]

from django.db import migrations


def fix_vote_content_types(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Vote = apps.get_model('secretballot', 'Vote')

    try:
        old_ct = ContentType.objects.get(app_label='mnmnwag', model='modernpost')
    except ContentType.DoesNotExist:
        return

    new_ct = ContentType.objects.get(app_label='wagtailcore', model='page')

    # Some (token, object_id) pairs already have a vote under new_ct (the user
    # voted from a route that used plain Page objects). For each old_ct vote,
    # delete it if a new_ct vote already exists for the same (token, object_id),
    # else move it.
    for vote in Vote.objects.filter(content_type=old_ct):
        if Vote.objects.filter(content_type=new_ct, token=vote.token, object_id=vote.object_id).exists():
            vote.delete()
        else:
            vote.content_type = new_ct
            vote.save()


class Migration(migrations.Migration):
    """
    MN MN MN MN MN
    Consolidate all votes to wagtailcore.page. Some votes were stored against
    mnmnwag.modernpost (from routes that returned ModernPost querysets); this
    moves them all to wagtailcore.page for consistency.
    """

    dependencies = [
        ('mnmnwag', '0047_alter_complexpage_body'),
        ('secretballot', '0003_alter_vote_table'),
    ]

    operations = [migrations.RunPython(fix_vote_content_types, migrations.RunPython.noop)]

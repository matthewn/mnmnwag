from django.db import migrations


class Migration(migrations.Migration):
    """
    MN MN MN MN MN
    Fixes a missing migration in django-secretballot: Vote.Meta explicitly sets
    db_table = "secretballot_vote", which is also the default, but the upstream
    migrations never recorded this. Beginning somehwere in the 4.x timeframe,
    Django's autodetector detects the discrepancy and perpetually wants to
    generate this migration. We record the state change here without issuing
    any SQL, since the table is already correctly named.
    """

    dependencies = [
        ("secretballot", "0002_auto_20200328_0249"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterModelTable(
                    name="vote",
                    table="secretballot_vote",
                ),
            ],
            database_operations=[],
        ),
    ]

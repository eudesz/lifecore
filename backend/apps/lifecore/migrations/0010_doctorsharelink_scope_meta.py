from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lifecore', '0009_conditions_and_links'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctorsharelink',
            name='scope_meta',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]



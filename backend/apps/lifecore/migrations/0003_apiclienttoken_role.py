from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lifecore', '0002_apiclienttoken'),
    ]

    operations = [
        migrations.AddField(
            model_name='apiclienttoken',
            name='role',
            field=models.CharField(choices=[('patient', 'patient'), ('doctor', 'doctor'), ('admin', 'admin')], default='patient', max_length=16),
        ),
    ]

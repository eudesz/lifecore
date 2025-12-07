from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('lifecore', '0007_memorysemantic_memoryepisode'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # TimelineEvent enhancements
        migrations.AddField(
            model_name='timelineevent',
            name='category',
            field=models.CharField(default='general', max_length=32),
        ),
        migrations.AddField(
            model_name='timelineevent',
            name='severity',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='timelineevent',
            name='related_conditions',
            field=models.JSONField(default=list, blank=True),
        ),
        migrations.AddField(
            model_name='timelineevent',
            name='data_summary',
            field=models.JSONField(default=dict, blank=True),
        ),

        # Treatment models
        migrations.CreateModel(
            name='Treatment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('medication_type', models.CharField(max_length=64)),
                ('condition', models.CharField(max_length=64)),
                ('dosage', models.CharField(max_length=128)),
                ('frequency', models.CharField(max_length=64)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('active', 'active'), ('discontinued', 'discontinued'), ('replaced', 'replaced'), ('completed', 'completed')], default='active', max_length=32)),
                ('reason', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TreatmentLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduled_date', models.DateTimeField()),
                ('taken_date', models.DateTimeField(blank=True, null=True)),
                ('taken', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('treatment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='lifecore.treatment')),
            ],
        ),
        migrations.CreateModel(
            name='TreatmentProgress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evaluation_date', models.DateField()),
                ('metrics', models.JSONField(default=dict)),
                ('effectiveness_score', models.IntegerField()),
                ('side_effects', models.TextField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('treatment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress', to='lifecore.treatment')),
            ],
        ),
        migrations.AddIndex(
            model_name='treatment',
            index=models.Index(fields=['user', 'condition', 'status'], name='lifecore_tr_user_co_1a75b7_idx'),
        ),
        migrations.AddIndex(
            model_name='treatment',
            index=models.Index(fields=['start_date'], name='lifecore_tr_start_d_7b8e1f_idx'),
        ),
        migrations.AddIndex(
            model_name='treatmentlog',
            index=models.Index(fields=['scheduled_date'], name='lifecore_tr_schedu_7f7e1b_idx'),
        ),
        migrations.AddIndex(
            model_name='treatmentlog',
            index=models.Index(fields=['taken'], name='lifecore_tr_taken_2a0c0a_idx'),
        ),
        migrations.AddIndex(
            model_name='treatmentprogress',
            index=models.Index(fields=['evaluation_date'], name='lifecore_tr_evalua_8c0f8a_idx'),
        ),
    ]



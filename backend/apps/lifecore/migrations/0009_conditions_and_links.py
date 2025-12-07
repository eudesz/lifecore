from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lifecore', '0008_treatments_and_timeline_enhancements'),
    ]

    operations = [
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=64, unique=True)),
                ('name', models.CharField(max_length=128)),
                ('color', models.CharField(default='#64748b', max_length=16)),
                ('aliases', models.JSONField(blank=True, default=list)),
            ],
        ),
        migrations.CreateModel(
            name='EventCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('condition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_links', to='lifecore.condition')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conditions_link', to='lifecore.timelineevent')),
            ],
            options={
                'unique_together': {('event', 'condition')},
            },
        ),
        migrations.AddIndex(
            model_name='eventcondition',
            index=models.Index(fields=['condition'], name='lifecore_ev_conditi_1b2a5e_idx'),
        ),
        migrations.AddIndex(
            model_name='eventcondition',
            index=models.Index(fields=['event'], name='lifecore_ev_event_7c5b9a_idx'),
        ),
        migrations.CreateModel(
            name='TreatmentCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('condition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='treatment_links', to='lifecore.condition')),
                ('treatment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='condition_links', to='lifecore.treatment')),
            ],
            options={
                'unique_together': {('treatment', 'condition')},
            },
        ),
        migrations.AddIndex(
            model_name='treatmentcondition',
            index=models.Index(fields=['condition'], name='lifecore_tr_conditi_7f5d0a_idx'),
        ),
        migrations.AddIndex(
            model_name='treatmentcondition',
            index=models.Index(fields=['treatment'], name='lifecore_tr_treatme_b8cf2c_idx'),
        ),
    ]



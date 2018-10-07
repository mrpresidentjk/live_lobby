# Generated by Django 2.1.2 on 2018-10-07 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_auto_20180928_0025'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='engagement_type',
            field=models.CharField(choices=[('COMPETITIVE', 'Competitive'), ('CASUAL', 'Casual')], default='CASUAL', max_length=25),
        ),
        migrations.AddField(
            model_name='event',
            name='is_booked',
            field=models.BooleanField(default=False),
        ),
    ]
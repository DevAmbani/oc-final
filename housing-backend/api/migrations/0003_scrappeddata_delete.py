# Generated by Django 5.1.4 on 2025-01-12 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_openaianalysis_scrappeddata_issue'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrappeddata',
            name='delete',
            field=models.BooleanField(default=False),
        ),
    ]

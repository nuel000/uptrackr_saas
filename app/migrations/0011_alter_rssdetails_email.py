# Generated by Django 4.2.4 on 2024-06-10 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_alter_cancelledsubscription_event_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rssdetails',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]

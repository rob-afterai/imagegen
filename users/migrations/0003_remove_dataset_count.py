# Generated by Django 4.1 on 2022-11-20 16:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_dataset_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataset',
            name='count',
        ),
    ]

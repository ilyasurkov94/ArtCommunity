# Generated by Django 2.2.19 on 2021-09-04 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='created',
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
    ]

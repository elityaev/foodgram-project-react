# Generated by Django 3.2.13 on 2022-06-18 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0004_auto_20220618_1751'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='unique_follow',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_follow'),
        ),
    ]
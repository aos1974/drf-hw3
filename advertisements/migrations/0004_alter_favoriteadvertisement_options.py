# Generated by Django 4.1.1 on 2022-09-18 14:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advertisements', '0003_favoriteadvertisement_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favoriteadvertisement',
            options={'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранные объявления'},
        ),
    ]

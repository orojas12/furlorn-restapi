# Generated by Django 3.2.9 on 2021-12-17 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_pet_microchip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pet',
            name='microchip',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]

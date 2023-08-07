# Generated by Django 4.2.4 on 2023-08-07 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grafxapp', '0004_alter_node_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='graphproperties',
            name='average_degree',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='graphproperties',
            name='clustering_coefficient',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='graphproperties',
            name='diameter',
            field=models.IntegerField(default=0),
        ),
    ]

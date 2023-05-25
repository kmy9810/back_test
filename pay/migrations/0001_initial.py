# Generated by Django 4.2.1 on 2023-05-25 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('supplied_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('point', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveIntegerField(default=0)),
                ('type', models.CharField(max_length=50)),
                ('is_subscribe', models.BooleanField(default=False)),
                ('start_subscribe_at', models.DateTimeField(auto_now_add=True)),
                ('restart_subscribe_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('duration', models.IntegerField(default=0)),
            ],
        ),
    ]

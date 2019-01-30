# Generated by Django 2.1.4 on 2019-01-30 10:34

from django.db import migrations, models
import django.db.models.deletion
import litigations.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Litigation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('release_no', models.CharField(max_length=15, unique=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('respondents', models.CharField(max_length=1024)),
                ('content', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=2000)),
                ('reference_text', models.CharField(max_length=2000)),
                ('litigation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='litigations.Litigation')),
            ],
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_text', models.CharField(blank=True, max_length=1024, null=True)),
                ('priority', models.IntegerField(default=6, validators=[litigations.models.is_positive])),
                ('litigation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='litigations.Litigation')),
            ],
        ),
    ]

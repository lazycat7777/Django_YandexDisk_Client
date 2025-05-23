# Generated by Django 5.1.8 on 2025-04-22 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Имя')),
                ('type', models.CharField(choices=[('file', 'Файл'), ('dir', 'Папка')], max_length=255, verbose_name='Тип')),
                ('path', models.CharField(db_index=True, max_length=255, unique=True, verbose_name='Путь')),
                ('created', models.DateTimeField(db_index=True, verbose_name='Дата создания')),
                ('modified', models.DateTimeField(db_index=True, verbose_name='Дата модификации')),
            ],
            options={
                'verbose_name': 'Ресурс',
                'verbose_name_plural': 'Ресурсы',
                'indexes': [models.Index(fields=['path'], name='yandex_disk_path_d25601_idx'), models.Index(fields=['created'], name='yandex_disk_created_13c373_idx'), models.Index(fields=['modified'], name='yandex_disk_modifie_d19895_idx')],
            },
        ),
    ]

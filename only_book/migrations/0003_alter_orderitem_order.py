# Generated by Django 5.1.3 on 2024-11-29 00:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('only_book', '0002_alter_author_birth_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_item', to='only_book.order'),
        ),
    ]
# Generated by Django 5.1.4 on 2025-06-07 07:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0017_product_low_stock_threshold_productstock'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='productstock',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='productstock',
            name='color_variant',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='products.colorvariant'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='productstock',
            unique_together={('product', 'size_variant', 'color_variant')},
        ),
    ]

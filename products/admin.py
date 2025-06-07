from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(Coupon)

class ProductImageAdmin(admin.StackedInline):
    model = ProductImage

class ProductStockAdmin(admin.StackedInline):
    model = ProductStock
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'price', 'get_stock_status']
    inlines = [ProductImageAdmin, ProductStockAdmin]

    def get_stock_status(self, obj):
        low_stock = ProductStock.objects.filter(product=obj, quantity__lte=obj.low_stock_threshold).exists()
        out_of_stock = ProductStock.objects.filter(product=obj, quantity=0).exists()
        if out_of_stock:
            return "Out of Stock"
        elif low_stock:
            return "Low Stock"
        return "In Stock"
    get_stock_status.short_description = 'Stock Status'

@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):
    list_display = ['color_name', 'price']
    model = ColorVariant

@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    list_display = ['size_name', 'price', 'order']
    model = SizeVariant

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(ProductReview)
admin.site.register(ProductStock)
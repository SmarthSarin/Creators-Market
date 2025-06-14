from django.db import models
from base.models import BaseModel
from django.utils.text import slugify
from django.utils.html import mark_safe
from django.contrib.auth.models import User # Or your Seller model

# Create your models here.


class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category_image = models.ImageField(upload_to="catgories")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.category_name


class ColorVariant(BaseModel):
    color_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.color_name


class SizeVariant(BaseModel):
    size_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    order = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.size_name


class Product(BaseModel):
    parent = models.ForeignKey(
        'self', related_name='variants', on_delete=models.CASCADE, blank=True, null=True)
    product_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = models.IntegerField()
    product_desription = models.TextField()
    color_variant = models.ManyToManyField(ColorVariant, blank=True)
    size_variant = models.ManyToManyField(SizeVariant, blank=True)
    newest_product = models.BooleanField(default=False)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products_for_sale', null=True, blank=True) # Example
    low_stock_threshold = models.PositiveIntegerField(default=5, help_text="Alert when stock falls below this number")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.product_name

    def get_product_price_by_size(self, size):
        return self.price + SizeVariant.objects.get(size_name=size).price

    def get_rating(self):
        total = sum(int(review['stars']) for review in self.reviews.values())

        if self.reviews.count() > 0:
            return total / self.reviews.count()
        else:
            return 0

    def get_order_count(self):
        from accounts.models import OrderItem
        return OrderItem.objects.filter(product=self).count()

    def is_low_stock(self, size_variant=None):
        if size_variant:
            stock = ProductStock.objects.filter(product=self, size_variant=size_variant).first()
            return stock and stock.quantity <= self.low_stock_threshold
        return False

    def is_out_of_stock(self, size_variant=None):
        if size_variant:
            stock = ProductStock.objects.filter(product=self, size_variant=size_variant).first()
            return not stock or stock.quantity <= 0
        return False

    def get_stock_quantity(self, size_variant=None):
        if size_variant:
            stock = ProductStock.objects.filter(product=self, size_variant=size_variant).first()
            return stock.quantity if stock else 0
            return 0


class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='product')

    def img_preview(self):
        return mark_safe(f'<img src="{self.image.url}" width="500"/>')


class Coupon(BaseModel):
    coupon_code = models.CharField(max_length=10)
    is_expired = models.BooleanField(default=False)
    discount_amount = models.IntegerField(default=100)
    minimum_amount = models.IntegerField(default=500)


class ProductReview(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    stars = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    content = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_reviews", blank=True)
    dislikes = models.ManyToManyField(User, related_name="disliked_reviews", blank=True)

    def like_count(self):
        return self.likes.count()

    def dislike_count(self):
        return self.dislikes.count()


class Wishlist(BaseModel):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    product=models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by")
    size_variant=models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True,
                                     blank=True, related_name="wishlist_items")

    added_on=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=('user', 'product', 'size_variant')

    def __str__(self) -> str:
        return f'{self.user.username} - {self.product.product_name} - {self.size_variant.size_name if self.size_variant else "No Size"}'


class ProductStock(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock')
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'size_variant')

    def __str__(self):
        return f"{self.product.product_name} - {self.size_variant.size_name}: {self.quantity}"

    def is_low_stock(self):
        return self.quantity <= self.product.low_stock_threshold

    def is_out_of_stock(self):
        return self.quantity <= 0

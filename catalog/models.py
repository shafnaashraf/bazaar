from django.db import models

from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length = 140 , unique = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now= True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name
    
    def save(self , *args, **kwargs):
        if not self.slug:            # auto-fill slug from name
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    # ForeignKey = many-to-one. PROTECT stops deleting a category that has products.
    # related_name lets us go the other way: category.products.all()
    category = models.ForeignKey(Category, on_delete= models.PROTECT, related_name="products")

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length= 220, unique= True, blank= True)
    description = models.TextField(blank= True)

    price = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(Decimal("0.00"))],
    )

    stock_quantity = models.PositiveBigIntegerField(default= 0)
    is_active = models.BooleanField(default= True)
    created_at = models.DateTimeField(auto_now_add= True)
    updated_at = models.DateTimeField(auto_now= True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["is_active"])]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def in_stock(self) -> bool:
        return self.stock_quantity > 0
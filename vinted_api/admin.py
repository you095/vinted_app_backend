from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Product, ProductImage, Review, Message, Favorite, Transaction, Payment

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_verified', 'location', 'date_joined')
    list_filter = ('is_verified', 'is_staff', 'is_active', 'location')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('profile_picture', 'bio', 'location', 'phone_number', 'is_verified')}),
    )

# Product Image Inline for Product Admin
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'price', 'category', 'is_sold', 'created_at')
    list_filter = ('is_sold', 'category', 'created_at')
    search_fields = ('title', 'description', 'seller__username')
    inlines = [ProductImageInline]

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent']  # Display the category name and its parent
    search_fields = ['name']  # Allow searching by category name
    list_filter = ['parent']  # Allow filtering by parent category


# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'seller', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer__username', 'seller__username', 'comment')

# Message Admin
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'is_read', 'timestamp')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__username', 'receiver__username', 'content')

# Favorite Admin
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__title')

# Transaction Admin
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'product', 'amount', 'status', 'transaction_date')
    list_filter = ('status', 'transaction_date')
    search_fields = ('buyer__username', 'product__title')

# Payment Admin
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'payment_method', 'payment_status', 'payment_date')
    list_filter = ('payment_method', 'payment_status', 'payment_date')

# Register User with custom admin
admin.site.register(User, CustomUserAdmin)

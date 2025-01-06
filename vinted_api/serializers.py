from rest_framework import serializers
from .models import ProductImage,    Category, Product
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

def compress_image(image):
    img = Image.open(image)
    img = img.convert('RGB')  # Ensure compatibility
    output = BytesIO()
    img.save(output, format='JPEG', quality=75)  # Adjust quality as needed
    output.seek(0)
    return InMemoryUploadedFile(output, 'ImageField', image.name, 'image/jpeg', len(output.getvalue()), None)

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image']

    def create(self, validated_data):
        image = validated_data.pop('image')
        compressed_image = compress_image(image)
        product_image = ProductImage.objects.create(image=compressed_image, **validated_data)
        return product_image

class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'subcategories']

    def get_subcategories(self, obj):
        # Recursively serialize subcategories
        subcategories = obj.subcategories.all()
        return CategorySerializer(subcategories, many=True).data

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False)
    categoryId = serializers.IntegerField(write_only=True)
    subcategoryId = serializers.IntegerField(write_only=True)
    seller = serializers.PrimaryKeyRelatedField(read_only=True)  # Make seller read-only
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'condition', 'category', 
                 'images', 'is_sold', 'created_at', 'categoryId', 'subcategoryId', 'seller']
        read_only_fields = ['is_sold', 'created_at']

    def create(self, validated_data):
        # Extract category IDs
        category_id = validated_data.pop('categoryId', None)
        subcategory_id = validated_data.pop('subcategoryId', None)
        
        # Set the category to the subcategory
        if subcategory_id:
            validated_data['category_id'] = subcategory_id
        
        # Set the seller to the current user
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)



from rest_framework import serializers
from .models import ProductImage,    Category, Product, Condition
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
    categoryId = serializers.IntegerField(write_only=True, required=False)
    subcategoryId = serializers.IntegerField(write_only=True, required=False)
    seller = serializers.PrimaryKeyRelatedField(read_only=True)  # Make seller read-only
    condition = serializers.PrimaryKeyRelatedField(queryset=Condition.objects.all(), required=False)
    title = serializers.CharField(required=False)  # Make title optional
    description = serializers.CharField(required=False)  # Make description optional
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)  # Make price optional

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price', 
            'condition', 'category', 'images', 'is_sold', 
            'created_at', 'categoryId', 'subcategoryId', 
            'seller'
        ]
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
        
        # Create the product
        product = super().create(validated_data)
        
        return product

    def to_representation(self, instance):
        # Get the default representation
        representation = super().to_representation(instance)
        
        # Add condition details
        if instance.condition:
            representation['condition'] = {
                'id': instance.condition.id,
                'name': instance.condition.name,
                'display_name': instance.condition.display_name,
                'description': instance.condition.description
            }
            
        # Add seller details
        if instance.seller:
            representation['seller'] = {
                'id': instance.seller.id,
                'username': instance.seller.username,
                'email': instance.seller.email
            }
            
        return representation

class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = ['id', 'name', 'display_name', 'description', 'order']



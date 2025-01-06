from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import ProductImageSerializer, compress_image, CategorySerializer, ProductSerializer
from vinted_backend.authentication.authentication import IsVintedAuthenticated
from .models import User, ProductImage, Category
from rest_framework import status
import traceback
import json


@api_view(['GET'])
@permission_classes([IsVintedAuthenticated])
def get_categories(request):
    categories = Category.objects.filter(parent__isnull=True)  # Get root categories
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


# Create your views here.
@api_view(['POST'])
@permission_classes([IsVintedAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_product_images(request):
    try:
        user = request.user
        product_id = request.data.get('product')
        if not product_id:
            return Response({'error': 'Product ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if 'image' field is present and if it contains multiple files
        images = request.FILES.getlist('image')
        if not images:
            return Response({'error': 'At least one image is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Process each image
        created_images = []
        for image in images:
            # Compress the image if necessary
            compressed_image = compress_image(image)
            
            # Create the ProductImage instance
            product_image = ProductImage.objects.create(product_id=product_id, image=compressed_image)
            created_images.append(ProductImageSerializer(product_image).data)

        return Response(created_images, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsVintedAuthenticated])
def dummy_data(request):
    # Print authenticated user information
    print("Authenticated User:", request.auth)  # Print the decoded JWT token
    
    data = {
        'items': [
            {
                'id': 1,
                'title': 'Vintage Denim Jacket',
                'price': 29.99,
                'description': 'Classic blue denim jacket in excellent condition',
                'size': 'M',
                'brand': 'Levi\'s'
            },
            {
                'id': 2,
                'title': 'Nike Running Shoes',
                'price': 45.00,
                'description': 'Barely used running shoes, very comfortable',
                'size': '42',
                'brand': 'Nike'
            },
            {
                'id': 3,
                'title': 'Summer Dress',
                'price': 15.50,
                'description': 'Floral pattern summer dress',
                'size': 'S',
                'brand': 'H&M'
            }
        ],
        'auth_info': {
            'token_data': request.auth,  # Include token data in response
            'user': str(request.user) if request.user else None  # Include user info in response
        }
    }
    return Response(data)

@api_view(['POST'])
@permission_classes([IsVintedAuthenticated])
def register_user(request):
    try:
        token_data = request.auth
        print(token_data)
        
        # Extract user information from token
        email = token_data.get('email')
        first_name = token_data.get('given_name', '')
        last_name = token_data.get('family_name', '')
        
        # Try to get existing user or create new one
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True
            }
        )
        
        if not created:
            print("***********************User exists, updating it with email:", email)
            # Update existing user's information
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            
            # Update additional fields if provided in request
            if request.data:
                if 'bio' in request.data:
                    user.bio = request.data['bio']
                if 'location' in request.data:
                    user.location = request.data['location']
                if 'phone_number' in request.data:
                    user.phone_number = request.data['phone_number']
                if 'profile_picture' in request.FILES:
                    user.profile_picture = request.FILES['profile_picture']
            
            user.save()
        else:
            print("*************User does not exist, creating it with email:", email)
        
        response_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': user.bio,
            'location': user.location,
            'phone_number': user.phone_number,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
            'is_verified': user.is_verified,
            'created': created
        }
        
        return Response(response_data, 
                      status=status.HTTP_201_CREATED if created 
                      else status.HTTP_200_OK)
    
    except Exception as e:
        # Get the full stack trace
        stack_trace = traceback.format_exc()
        
        # Print the stack trace to server console
        print("Error in register_user:")
        print(stack_trace)
        
        # Prepare detailed error response
        error_response = {
            'error': str(e),
            'type': type(e).__name__,
            'detail': stack_trace.split('\n'),
            'location': 'register_user endpoint'
        }
        
        return Response(
            error_response,
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([IsVintedAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_product(request):
    try:
        user = request.user
        print("Creating product for user:", user.id)
        
        # Create the product
        serializer = ProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            product = serializer.save()
            print("Product created with seller:", product.seller_id)
            
            # Handle images
            created_images = []
            images_data = request.FILES.getlist('images[]')
            for image in images_data:
                try:
                    product_image = ProductImage.objects.create(
                        product=product,
                        image=image
                    )
                    created_images.append({
                        'id': product_image.id,
                        'url': product_image.image.url
                    })
                except Exception as img_error:
                    print(f"Error processing image: {str(img_error)}")
                    continue
            
            # Add images to the response
            response_data = serializer.data
            response_data['images'] = created_images
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        stack_trace = traceback.format_exc()
        print("Error in create_product:")
        print(stack_trace)
        print("Request data:", request.data)
        
        error_response = {
            'error': str(e),
            'type': type(e).__name__,
            'detail': stack_trace.split('\n'),
            'location': 'create_product endpoint'
        }
        
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

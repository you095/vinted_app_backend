from django.urls import path
from vinted_api.views import (
    dummy_data, register_user, upload_product_images, 
    get_categories, create_product
)

urlpatterns = [
    path('dummy/', dummy_data, name='dummy-data'),
    path('register/', register_user, name='register-user'),
    path('upload-product-images/', upload_product_images, name='upload-product-images'),
    path('get-categories/', get_categories, name='get-categories'),
    path('create-product/', create_product, name='create-product'),
]


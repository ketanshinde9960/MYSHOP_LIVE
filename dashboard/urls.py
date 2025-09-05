from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dashboard'),
    path('product/', views.product, name='product'),
    path('update/<int:id>', views.update_product, name='update-product'),
    path('delete/<int:id>', views.delete_product, name='delete-product')
]

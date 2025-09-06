from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Home & User Pages
    path('', views.home, name="home"),
    path('profile/', views.user_profile, name="profile"),
    path('profile-edit/', views.user_profile_edit, name="profile-edit"),
    path('about/', views.about, name="about"),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('ajax/category/<slug:slug>/', views.category_products_ajax, name='category_products_ajax'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),


    # Checkout & Payment
    path("checkout/", views.checkout, name="checkout"),
    path("pay/", views.pay, name="pay"),
    path('payment-success/', views.payment_success, name='payment_success'),
    # path('make_payment/', views.make_payment, name='make_payment'),
    

    # Cart Management
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.user_cart_products, name='cart'),
    path('update-cart/<int:cart_item_id>/', views.update_cart, name='update-cart'),
    path('update-checkout/<int:cart_item_id>/', views.update_checkout, name='update-checkout'),
    path('delete-cart-item/<int:cart_item_id>/', views.delete_cart_item, name='delete-cart-item'),
    path('delete-checkout-item/<int:cart_item_id>/', views.delete_checkout_item, name='delete-checkout-item'),

    # Wishlist
    path('add-to-wishlist/<int:id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.user_wishlist_products, name='wishlist'),
    path('move-to-cart/<int:wishlist_item_id>/', views.move_to_cart, name='move-to-cart'),
    path('move-to-wishlist/<int:cart_item_id>/', views.move_to_wishlist, name='move-to-wishlist'),
    path('delete-wishlist-item/<int:wishlist_item_id>/', views.delete_wishlist_item, name='delete-wishlist-item'),
    path('delete-all-wishlist-items/', views.delete_all_wishlist_items, name='delete-all-wishlist-items'),

    # Orders
    path('move-to-order/', views.move_to_order, name='move-to-order'),
    path('order/', views.user_order_products, name='order'),
    path('create-order/', views.create_order, name='create_order'),

    # Address
    path('user-address/', views.user_address, name='user-address'),

    # Authentication (OTP)
    path('auth/', views.handle_otp, name="auth"),
]

# Serving media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

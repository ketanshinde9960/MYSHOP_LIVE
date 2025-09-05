# your_app/context_processors.py
from .models import CartItem, WishListItem

def cart_items_count(request):
    if request.user.is_authenticated:
        cart_items_count = CartItem.objects.filter(cart__user=request.user).count()
    else:
        cart_items_count = 0

    return {'cart_items_count': cart_items_count}

def wishlist_items_count(request):
    if request.user.is_authenticated:
        wishlist_items_count = WishListItem.objects.filter(wishlist__user=request.user).count()
    else:
        wishlist_items_count = 0

    return {'wishlist_items_count': wishlist_items_count}

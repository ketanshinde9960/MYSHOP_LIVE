from django.contrib import admin
from .models import Product, Category, Order, OrderItem,Address, Cart, CartItem, WishList,WishListItem,ContactMessage # import only what's needed


# Custom admin for Order
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_address', 'payment_status', 'amount', 'created_at')
    list_filter = ('payment_status', 'created_at')
    search_fields = ('user__username', 'user__email')

    def get_address(self, obj):
        # Get latest address linked to the order's user
        address = Address.objects.filter(user=obj.user).last()
        if address:
            return f"{address.username}, {address.mobile}, {address.address}, {address.city}, {address.state}, {address.zip_code}"
        return "No Address"
    get_address.short_description = 'Shipping Address'

# Register models
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(WishList)
admin.site.register(WishListItem)
admin.site.register(Order, OrderAdmin)  # ← customized Order view
admin.site.register(OrderItem)
admin.site.register(Address)
admin.site.register(ContactMessage)
admin.site.register(Category)

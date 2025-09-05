from django.db import models
from django.contrib.auth.models import User
# import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Auth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
#------------------------------------------------------------------------------------------------------------

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    username = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15, null=True, blank=True)  # 💡 limited to 15 chars, standard for mobile
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)  # 💡 Pincode length is usually 6 in India

    def __str__(self):
        return f"{self.username} - {self.city}, {self.state}"

 ################################################################################################   

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon_class = models.CharField(max_length=100, blank=True)  

    def __str__(self):
        return self.name

#################################################################################

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    bestSeller = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.name


#####################################################################################

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(default="test@example.com")
    products = models.ManyToManyField('Product', through='OrderItem')
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, default="Pending")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    order_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)

    def total_cart_value(self):
        return sum(item.total_price() for item in self.orderitem_set.all())

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            # Generate order ID and calculate amount
            self.order_id = f"ORD-{self.pk:05d}"
            self.amount = self.total_cart_value()
            super().save(update_fields=["order_id", "amount"])

            # Send confirmation email to customer
            # send_mail(
            #     subject=f"Your Order {self.order_id} has been placed",
            #     message=f"Hi {self.user.username},\n\n"
            #             f"Thank you for your order!\n"
            #             f"Order ID: {self.order_id}\n"
            #             f"Total Amount: ₹{self.amount}\n\n"
            #             "We will notify you when your order is shipped.\n\n"
            #             "Best regards,\nGurudatta Sales",
            #     from_email=settings.EMAIL_HOST_USER,
            #     recipient_list=[self.user.email],
            #     fail_silently=False,
            # )


    def __str__(self):
        return f"Order #{self.pk} by {self.user.username} - ₹{self.amount}"

    
#######################################################################################

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        """Return total price of this order item (quantity × product price)."""
        return self.product.price * self.quantity  

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.pk}"

#####################################################################################

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem')

    def __str__(self):
        return f"Cart for {self.user.username}"
#################################################################################
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sub_total = models.DecimalField(null=True, max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
         unique_together = ('cart', 'product')

    def __str__(self): 
        return f"{self.quantity} x {self.product.name} in Cart for {self.cart.user.username}"
############################################################################################
# wishlist cart
class WishList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='WishListItem')

    def __str__(self):
        return f"WishList for {self.user.username}"
##################################################################################
# wishlist items
class WishListItem(models.Model):
    wishlist = models.ForeignKey(WishList, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} in WishList #{self.wishlist.pk}"
    

###############################################################################################
class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"


###############################################################################################
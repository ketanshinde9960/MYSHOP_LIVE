from django.utils import timezone
import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.db.models import Q
from .models import *
from .utils import send_order_confirmation_email, send_email_verification_OTP
import random  # For generating a random OTP
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage, Cart, Order, Product
import razorpay
from django.http import JsonResponse
import time
from .models import Category
from .forms import AddressForm
from django.contrib import messages



from django.template.loader import render_to_string






# Create your views here.

def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()  

    if request.GET.get('search'):
        products = products.filter(name__icontains=request.GET.get('search'))

    context = {
        'products': products,
        'categories': categories,  
    }
    return render(request, 'index.html', context)
    ############################################################################################################


############################################################################################################



@login_required(login_url='/login/') #redirect when user is not logged in
def user_profile(request):
    # Access the current user's data
    user_data = {
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        # Add other user-related data as needed
    }
    # Check if the user has an address
    user_address = Address.objects.filter(user=request.user).first()

    context = {
        'user_data': user_data,
        'user_address': user_address,
    }

    return render(request, 'profile.html', context)
############################################################################################################
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .models import Address, Order

@login_required
def user_profile_edit(request):
    user = request.user

    # Prepare user data for template
    user_data = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }

    # ✅ Fix for MultipleObjectsReturned
    # ✅ Always fetch the latest address for the logged-in user
    user_address = Address.objects.filter(user=user).order_by('-id').first()
    if not user_address:
        user_address = Address.objects.create(
            user=user,
            email=user.email,
            username=user.username,
            address='',
            city='',
            state='',
            zip_code=''
        )


    # Fetch latest order
    latest_order = Order.objects.filter(user=user).order_by('-id').first()
    order_id = latest_order.id if latest_order else None
    total_cart_value = getattr(latest_order, 'total_cart_value', 0)

    if request.method == 'POST':
        # ----- Update User Details & Password -----
        if 'user_details_form' in request.POST:
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')

            # Prevent duplicate username
            if User.objects.filter(username=username).exclude(id=user.id).exists():
                messages.warning(request, 'Username already taken. Choose another.')
                return redirect('profile-edit')

            # Update user fields
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name

            # Update password if provided
            if old_password and new_password:
                if user.check_password(old_password):
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'User details and password updated successfully.')
                else:
                    messages.warning(request, 'Old password does not match.')
                    return redirect('profile-edit')
            else:
                user.save()
                messages.success(request, 'User details updated successfully.')

        # ----- Update Address -----
        elif 'address_form' in request.POST:
            user_address.address = request.POST.get('address', '')
            user_address.mobile = request.POST.get('mobile', '')
            user_address.city = request.POST.get('city', '')
            user_address.state = request.POST.get('state', '')
            user_address.zip_code = request.POST.get('zip_code', '')
            user_address.username = request.POST.get('username', user.username)
            user_address.email = request.POST.get('email', user.email)
            user_address.save()
            messages.success(request, 'Address updated successfully.')

        return redirect('profile-edit')

    return render(request, 'profile_edit.html', {
        'user_data': user_data,
        'user_address': user_address,
        'order_id': order_id,
        'total_cart_value': total_cart_value
    })




#############################################################################################################
def about(request):
    return render(request, 'about.html')
############################################################################################################


def login_page(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
    
        user = User.objects.filter(email=email).first()

        if not user:
            messages.warning(request, 'Invalid email and password!')
            return redirect("/login/")
        
        # Use the check_password method to verify the password
        if not user.check_password(password):
            messages.warning(request, 'Invalid password. try again!!')
            return redirect("/login/")

        # authenticate() is not needed here, as you've already validated the credentials
        login(request, user)
        return redirect("/")
      
        # Try to get the related Auth instance using get()
        try:
            auth_instance = Auth.objects.get(user=user)
            if auth_instance.is_verified:
                # Your logic here if is_verified is True
                messages.success(request, 'Login successful.')
                return redirect("/")
            else:
                # Your logic here if is_verified is False
                return redirect("auth")

        except Auth.DoesNotExist:
            # If Auth object doesn't exist, handle the situation accordingly
            auth_instance = Auth.objects.create(user=user, is_verified=False)
            return redirect("auth")

    
    return render(request, 'login.html')
############################################################################################################



def logout_page(request):
    logout(request) 
    return redirect("/login/")
############################################################################################################


def register_page(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        for letter in first_name:
            isDigit = letter.isdigit()
            if isDigit:
                messages.warning(request, 'Please enter valid user name')
                return redirect('/register')

        # checking user is present in db
        user = User.objects.filter(username = username)

        if user.exists():
            messages.warning(request, 'Username is already taken by someone!')
            return redirect('/register')

        # insert user into db
        user = User.objects.create(
            first_name = first_name,
            last_name = last_name,
            username = username,
            email = email,
        )

        # pass convert into encrypted password 
        user.set_password(password)
        user.save()

        messages.success(request, 'Account created successfully!')
        return redirect("/login")

    return render(request, 'register.html') 
############################################################################################################


# verification
@login_required(login_url='/login/') #redirect when user is not logged in
def handle_otp(request):
    if not request.method == "POST":
        messages.info(request, "VERIFICATION STEP")

    if request.method == 'POST':
        # Check if the 'get-otp' button was clicked
        if 'get-otp' in request.POST:
            return send_otp(request)
        elif 'check' in request.POST:
            return verify_otp(request)
    return render(request, 'auth.html') 
############################################################################################################


def send_otp(request):
    code = str(random.randint(100000, 999999))
    # Store the OTP in the user's session
    request.session['generated_otp'] = code
    # Update the otp field using update()
    Auth.objects.filter(user=request.user).update(otp=code)
    
    client_email = request.user.email
    email_sent = send_email_verification_OTP(client_email, code)

    if email_sent:
        messages.success(request, f'Check Out! Verification code send on "{client_email}".')
    else:
        messages.warning(request, "Something wrong! mail failed.")

    print(f"otp : {code}")
    return redirect('auth')
############################################################################################################

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        correct_otp = request.session.get('generated_otp')

        if entered_otp == correct_otp:
            # Update the is_verified field using update()
            Auth.objects.filter(user=request.user).update(is_verified=True)
            # Redirect to a success page.
            messages.success(request, 'User Authentication successfully!')
            return redirect('home')
        else:
            messages.warning(request, 'Incorrect OTP. Please try again.')

        return redirect('auth')
    
    return render(request, 'auth.html')


############################################################################################################

# address
@login_required(login_url='/login/') #redirect when user is not logged in
def user_address(request):
    if request.method == "POST":
        email = request.POST.get('email')
        username = request.POST.get('username')
        mobile = request.POST.get("mobile")
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')

        address = Address(
            user = request.user,
            email = email,
            username = username,
            mobile=mobile,
            address = address,
            city = city,
            state = state,
            zip_code = zip_code
        )
        address.save()
        messages.success(request, 'Address added successfully!')
        return redirect("/checkout/")
    return redirect("/checkout/")

############################################################################################################



# add-to-cart
def add_to_cart(request, id):
    if not request.user.is_authenticated:
        # If the user is not authenticated, display a message and redirect to login
        messages.warning(request, "Please log in to add items to your cart.")
        return redirect('/login/')  # Change 'login' to the name of your login view

    product = get_object_or_404(Product, pk=id)
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    
    # Check if the product is already in the cart
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not item_created:
        # Product is already in the cart
        cart_item.quantity += 1
        cart_item.save()
        messages.warning(request, f"{product.name} quantity updated in your cart.")
    else:
        # Product added to the cart
        messages.success(request, f"{product.name} added to your cart.")
    
    return redirect('/') 
############################################################################################################
@login_required(login_url='/login/') #redirect when user is not logged in
def user_cart_products(request):
    user = request.user
    cart_items = CartItem.objects.filter(cart__user=user)

    # Calculate subtotal for each cart item
    for cart_item in cart_items:
        cart_item.sub_total = cart_item.product.price * cart_item.quantity

    # Calculate total cart value (sum of all subtotals)
    total_cart_value = sum(cart_item.sub_total for cart_item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_cart_value': total_cart_value,
    }


    return render(request, 'cart.html', context)
####################################################################################################################
@login_required(login_url='/login/') #redirect when user is not logged in
def update_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)

    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', 1))

        if new_quantity > 0 and new_quantity <= 10:  # Assuming max quantity is 10
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f"Quantity updated for {cart_item.product.name}.")

        else:
            messages.error(request, "Invalid quantity. Please enter a number between 1 and 10.")

    return redirect('/cart/')

####################################################################################################################
@login_required(login_url='/login/') #redirect when user is not logged in
def update_checkout(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)

    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity', 1))

        if new_quantity > 0 and new_quantity <= 10:  # Assuming max quantity is 10
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f"Quantity updated for {cart_item.product.name}.")

        else:
            messages.error(request, "Invalid quantity. Please enter a number between 1 and 10.")

    return redirect('/checkout/')
################################################################################################################
@login_required
def delete_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    
    # Deleting the cart item
    cart_item.delete()
    
    messages.success(request, f"{cart_item.product.name} removed from your cart.")
    
    return redirect('/cart/')
###############################################################################################################
# for checkout delete-checkout-item
@login_required
def delete_checkout_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    
    # Deleting the cart item
    cart_item.delete()
    
    messages.success(request, f"{cart_item.product.name} removed from your cart.")
    
    return redirect('/checkout/')
##############################################################################################################
# add-to-wishlist
@login_required(login_url='/login/')
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, pk=id)
    user = request.user
    wishlist, created = WishList.objects.get_or_create(user=user)

    # Check if the product is already in the wishlist
    wishlist_item, item_created = WishListItem.objects.get_or_create(wishlist=wishlist, product=product)

    if not item_created:
        # Product is already in the wishlist
        wishlist_item.quantity += 1
        wishlist_item.save()
        messages.warning(request, f"{product.name} quantity updated in your wishlist.")
    else:
        # Product added to the wishlist
        messages.success(request, f"{product.name} added to your wishlist.")

    return redirect('/')
###############################################################################################
@login_required(login_url='/login/') #redirect when user is not logged in
def user_wishlist_products(request):
    user = request.user
    wishlist_items = WishListItem.objects.filter(wishlist__user=user)

    # Calculate total wishlist value (sum of all prices)
    total_wishlist_value = sum(wishlist_item.product.price for wishlist_item in wishlist_items)

    context = {
        'wishlist_items': wishlist_items,
        'total_wishlist_value': total_wishlist_value,
    }

    return render(request, 'wishlist.html', context)
#################################################################################################
@login_required
def delete_wishlist_item(request, wishlist_item_id):
    wishlist_item = get_object_or_404(WishListItem, id=wishlist_item_id, wishlist__user=request.user)
    
    # Deleting the wishlist item
    wishlist_item.delete()
    
    messages.success(request, f"{wishlist_item.product.name} removed from your wishlist.")
    
    return redirect('/wishlist/')
##############################################################################################
@login_required
def delete_all_wishlist_items(request):
    user = request.user

    # Get the user's wishlist
    wishlist_items = WishListItem.objects.filter(wishlist__user=user)

    # Delete all wishlist items
    wishlist_items.delete()

    messages.success(request, "All items removed from your wishlist.")

    return redirect('/wishlist/')


##################################################################################################################################
@login_required
def move_to_cart(request, wishlist_item_id):
    wishlist_item = get_object_or_404(WishListItem, id=wishlist_item_id, wishlist__user=request.user)

    # Check if the product is already in the cart
    cart_item, cart_item_created = CartItem.objects.get_or_create(cart=request.user.cart, product=wishlist_item.product)

    if not cart_item_created:
        # Product is already in the cart
        messages.warning(request, f"{wishlist_item.product.name} product already added in your cart.")
    else:
        # Product added to the cart
        cart_item.quantity = 1  # Set the quantity to 1 for a new item
        cart_item.save()
        messages.success(request, f"{wishlist_item.product.name} added to your cart.")

    # Delete the wishlist item
    wishlist_item.delete()

    messages.success(request, f"{wishlist_item.product.name} removed from your wishlist.")

    return redirect('/wishlist/')

##################################################################################################################################
# for checkout move-to-wishlist 
@login_required
def move_to_wishlist(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)

    # Check if the product is already in the wishlist
    wishlist_item, wishlist_item_created = WishListItem.objects.get_or_create(
        wishlist=request.user.wishlist,
        product=cart_item.product
    )

    if not wishlist_item_created:
        # Product is already in the wishlist
        messages.warning(request, f"{cart_item.product.name} product already in your wishlist.")
    else:
        # Product added to the wishlist
        wishlist_item.quantity = 1  # Set the quantity to 1 for a new item
        wishlist_item.save()
        messages.success(request, f"{cart_item.product.name} added to your wishlist.")

    # Delete the cart item
    cart_item.delete()

    messages.success(request, f"{cart_item.product.name} removed from your cart.")

    return redirect('/checkout/')

####################################################################################################################################

# for checkout page  move-to-order
from django.core.mail import send_mail
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

@login_required
def move_to_order(request):
    user = request.user
    cart_items = CartItem.objects.filter(cart__user=user)

    if not cart_items.exists():
        messages.warning(request, "No items in cart.")
        return redirect("cart")

    # Create new order
    order = Order.objects.create(user=user, payment_status="unpaid")

    total = 0
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity
        )
        total += item.product.price * item.quantity

    order.amount = total
    order.save()

    cart_items.delete()  # Empty cart

    # Get latest address from checkout
    latest_address = Address.objects.filter(user=user).order_by('-id').first()

    if latest_address and latest_address.email:
        customer_email = latest_address.email.strip()
        try:
            validate_email(customer_email)
            subject = f"Order Confirmation - #{order.id}"
            message = (
                f"Hello {latest_address.username},\n\n"
                f"Your order #{order.id} has been placed successfully.\n"
                f"Total Amount: ₹{order.amount}\n\n"
                "Thank you for shopping with us!"
            )

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [customer_email, settings.ADMIN_EMAIL],
                fail_silently=False
            )
        except ValidationError:
            print(f"Invalid customer email: {customer_email}")

    return redirect("pay")


# Redirect to pay view


##################################################################################################################
# #checkout 
# @login_required(login_url='/login/') #redirect when user is not logged in
# def checkout(request):
#     user = request.user
#     cart_items = CartItem.objects.filter(cart__user=user)

#     # Calculate subtotal for each cart item
#     for cart_item in cart_items:
#         cart_item.sub_total = cart_item.product.price * cart_item.quantity

#     # Calculate total cart value (sum of all subtotals)
#     total_cart_value = sum(cart_item.sub_total for cart_item in cart_items)

#     context = {
#         'cart_items': cart_items,
#         'total_cart_value': total_cart_value,
#     }
#     return render(request, 'checkout.html', context)

  ####################################################################################################
# @login_required(login_url='/login/')  # redirect when user is not logged in
# def checkout(request):
#     user = request.user
#     cart_items = CartItem.objects.filter(cart__user=user)

#     # Calculate subtotal for each cart item
#     for cart_item in cart_items:
#         cart_item.sub_total = cart_item.product.price * cart_item.quantity

#     # Calculate total cart value (sum of all subtotals)
#     total_cart_value = sum(cart_item.sub_total for cart_item in cart_items)

#     # Creating an order
#     order = Order.objects.create(user=user)

#     # Adding order items (the products and their quantity) to the order
#     for cart_item in cart_items:
#         OrderItem.objects.create(
#             order=order,
#             product=cart_item.product,
#             quantity=cart_item.quantity,
#             price=cart_item.product.price,
#         )

#     # Redirect to payment page with order info
#     context = {
#         'cart_items': cart_items,
#         'total_cart_value': total_cart_value,
#         'order': order,  # You can use this order object in the template
#     }
#     return render(request, 'pay.html', context)



# ##################################################################################--------------------------------------------------------------------------------

# # orders page
@login_required(login_url='/login/') #redirect when user is not logged in
def user_order_products(request):
    user = request.user
    order_items = OrderItem.objects.filter(order__user=user)

    # Get all addresses belonging to the user
    addresses = Address.objects.filter(user=user)

    context = {
        'order_items': order_items,
         'addresses': addresses,
    }

    return render(request, 'orders.html', context)



# def contact(request):
#     return render(request, 'contact.html')


############################################################################################

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # Store message in the database
        ContactMessage.objects.create(name=name, email=email, message=message)

        # Send email notification
        send_mail(
            subject=f"New Contact Message from {name}",
            message=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],  # Change to your email
            fail_silently=False,
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect("contact")

    return render(request, "contact.html")

#####################################################################################################

# def product_detail(request, id):
#     product = get_object_or_404(Product, id=id)
#     return render(request, 'product_detail.html', {'product': product})

###############################################################################################
#checkout 
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import CartItem, Address

@login_required(login_url='/login/')
def checkout(request):
    user = request.user
    cart_items = CartItem.objects.filter(cart__user=user)

    # Calculate subtotal for each cart item
    for cart_item in cart_items:
        cart_item.sub_total = cart_item.product.price * cart_item.quantity

    total_cart_value = sum(cart_item.sub_total for cart_item in cart_items)

    # ✅ Handle form POST to save address
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        zip_code = request.POST.get("zip_code")

        if all([email, username, mobile, address, city, state, zip_code]):
            Address.objects.create(
                user=user,
                email=email,
                username=username,
                mobile=mobile,
                address=address,
                city=city,
                state=state,
                zip_code=zip_code
            )
            return redirect("move-to-order")  # Or wherever you want to go next
        else:
            return render(request, "checkout.html", {
                "cart_items": cart_items,
                "total_cart_value": total_cart_value,
                "error": "❌ All fields are required."
            })

    # Initial GET request
    return render(request, "checkout.html", {
        'cart_items': cart_items,
        'total_cart_value': total_cart_value
    })

###########################################################################################################################
# @login_required
# def make_payment(request):
#     user = request.user
#     context = {}

#     # Fetch cart items
#     cart_items = CartItem.objects.filter(cart__user=user)
#     total_cart_value = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items)

#     # Get unpaid orders
#     orders = Order.objects.filter(user=user, payment_status="unpaid")
#     sum_amt = sum(order.amt for order in orders)
#     orderid = orders.first().order_id if orders.exists() else None

#     # 🟢 Debugging: Print before Razorpay call
#     print(f"✅ Total Amount: {sum_amt} INR, Order ID: {orderid}")

#     if sum_amt > 0 and orderid:
#         client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
        
#         # Convert to paise
#         amount_in_paise = int(sum_amt * 100)
#         print(f"🟢 Sending Amount to Razorpay: {sum_amt} INR, Converted to Paise: {amount_in_paise} paise")

#         # Create order
#         data = {"amount": amount_in_paise, "currency": "INR", "receipt": orderid}
#         payment = client.order.create(data=data)

#         # 🟢 Debugging: Check response
#         print(f"✅ Razorpay API Response: {payment}")

#         context.update({ 
#             'order_id': payment.get('id', None),
#             'total_cart_value': sum_amt,
#             'currency': payment.get('currency', 'INR'),
#             'key_id': settings.RAZORPAY_KEY_ID,
#         })
#     else:
#         print("🚨 No unpaid orders or total amount is zero.")
#         context['error'] = "No unpaid orders found or total amount is zero."
    
#     return render(request, 'pay.html', context)

################################################################################################################################
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
import razorpay
from .models import Order  # ✅ Make sure this is correct

@login_required
def pay(request):
    user = request.user

    # ✅ Get the most recent unpaid order
    order = Order.objects.filter(user=user, payment_status="unpaid").order_by('-id').first()

    if order and order.amount > 0:
        receipt_id = f"ORD-{order.id}"
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        amount_in_paise = int(order.amount * 100)

        try:
            # ✅ Create Razorpay order
            payment = client.order.create({
                "amount": amount_in_paise,
                "currency": "INR",
                "receipt": receipt_id,
            })

            # ✅ Save Razorpay order ID to our order
            order.razorpay_order_id = payment["id"]
            order.save()

        except Exception as e:
            print("❌ Razorpay Error:", e)
            return render(request, "pay.html", {
                "error": "Payment gateway error. Please try again later.",
                "amount": 0,
                "order_id": None,
                "total_cart_value": 0
            })

        context = {
            "order_id": payment["id"],
            "amount": order.amount,
            "total_cart_value": order.amount,
            "currency": payment.get("currency", "INR"),
            "key_id": settings.RAZORPAY_KEY_ID,
            "user": user
        }
        

    else:
        print("🚨 No valid unpaid order found.")
        context = {
            "amount": 0,
            "order_id": None,
            "total_cart_value": 0
        }

    return render(request, "pay.html", context)





################################################################################################################################
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_order(request):
    if request.method == "POST":
        # 🚀 Fetch unpaid orders & calculate total amount dynamically
        orders = Order.objects.filter(user=request.user, payment_status="unpaid")
        total_amount = sum(order.amt for order in orders) * 100  # Convert INR to paise
        
        if total_amount <= 0:
            return JsonResponse({"error": "No unpaid orders found!"}, status=400)

        currency = "INR"
        receipt = f"order_rcptid_{request.user.id}_{int(time.time())}"  # Unique receipt ID

        order_data = {
            "amount": total_amount,
            "currency": currency,
            "receipt": receipt,
            "payment_capture": 1  # Auto-capture
        }

        # ✅ Create an order with Razorpay
        razorpay_order = razorpay_client.order.create(order_data)

        print(f"✅ Razorpay Order Created: {razorpay_order}")  # Debugging

        # ✅ Save order details correctly in DB
        for order in orders:
            order.order_id = razorpay_order["id"]  # Update order_id for each unpaid order
            order.save()

        print(f"✅ Orders Updated in DB: {orders}")  # Debugging

        return JsonResponse({
            "order_id": razorpay_order["id"],
            "amount": total_amount / 100  # Convert back to INR
        })

    return JsonResponse({"error": "Invalid request method!"}, status=400)

    


##########################################################################################################################################

from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import razorpay
import json
from .models import Order

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        print("🟢 Payment Success View Called")

        try:
            raw_data = request.body.decode('utf-8')
            json_data = json.loads(raw_data)

            payment_id = json_data.get("razorpay_payment_id")
            order_id = json_data.get("razorpay_order_id")
            signature = json_data.get("razorpay_signature")

            print(f"✅ Received Data - Payment ID: {payment_id}, Order ID: {order_id}, Signature: {signature}")

            if not payment_id or not order_id or not signature:
                return JsonResponse({"error": "Missing payment data"}, status=400)

            # ✅ Razorpay verification
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })

            # ✅ Get and update order
            order = Order.objects.get(razorpay_order_id=order_id)
            order.payment_status = 'paid'
            order.save()

            print("✅ Payment Verified & Order Updated Successfully!")

            # ✅ Get shipping address from Address model
            address_obj = Address.objects.filter(user=order.user).first()
            if address_obj:
                phone = address_obj.mobile or "N/A"
                address_info = f"""{address_obj.address}
{address_obj.city}, {address_obj.state} - {address_obj.zip_code}"""
            else:
                phone = "N/A"
                address_info = "No address provided"

            # ✅ Send email to customer
            subject_customer = "Your Order is Confirmed! 🎉"
            message_customer = f"""Dear {order.user.username},

Your payment of ₹{order.amount} has been successfully processed.

Order ID: {order.razorpay_order_id}

Thank you for shopping with Elite Electronics!

Best Regards,
Elite Electronics Team
"""
            send_mail(
                subject_customer,
                message_customer,
                settings.EMAIL_HOST_USER,
                [order.user.email],
                fail_silently=False
            )

            # ✅ Send email to admin
            subject_admin = f"New Order Received: {order.order_id or order.razorpay_order_id}"
            message_admin = f"""A new order has been placed!

Customer: {order.user.username}
Email: {order.user.email}
Phone: {phone}

Shipping Address:
{address_info}

Order ID: {order.order_id or order.razorpay_order_id}
Amount: ₹{order.amount}
Payment Status: {order.payment_status.capitalize()}

Check the admin dashboard for full details.
"""
            send_mail(
                subject_admin,
                message_admin,
                settings.EMAIL_HOST_USER,
                [settings.ADMIN_EMAIL],
                fail_silently=False
            )

            return JsonResponse({"message": "Payment successful, email sent", "order_id": order.razorpay_order_id})

        except razorpay.errors.SignatureVerificationError as e:
            print(f"🚨 Razorpay Signature Verification Failed: {str(e)}")
            return JsonResponse({"error": "Payment verification failed"}, status=400)

        except Order.DoesNotExist:
            print("🚨 Order Not Found in Database!")
            return JsonResponse({"error": "Order not found"}, status=400)

        except Exception as e:
            print("❌ Unexpected Error:", str(e))
            return JsonResponse({"error": str(e)}, status=500)

    print("🚨 Invalid Request Method")
    return JsonResponse({"error": "Invalid request"}, status=400)


###################################################################################################################################################



def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, 'category_products.html', {
        'category': category,
        'products': products
    })



def category_products_ajax(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    
    html = render_to_string("partials/product_cards.html", {'products': products})
    
    return JsonResponse({'html': html})



def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'product_detail.html', {'product': product})




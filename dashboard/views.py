from django.shortcuts import render, redirect
from django.contrib import messages
from app.models import Product

# Create your views here.
def index(request):
    return render(request, 'dashboard.html')

def product(request):
    queryset = Product.objects.all()

    if request.method == 'POST':
        data = request.POST

        name = data.get('name')
        description = data.get('description')
        category = data.get('category')
        price = data.get('price')
        image = request.FILES.get('image')

        # Check if the checkbox is checked, set the value to True, otherwise, set it to False
        bestSeller = request.POST.get('bestSeller', False) == 'on'

        # Create a new Product instance and save it
        product = Product(
            name=name,
            description=description,
            category=category,
            price=price,
            image=image,
            bestSeller=bestSeller
        )
        product.save()
        # Add a success message with the product name
        messages.success(request, f'Product "{name}" added successfully!!')

    context = {'products': queryset}
    return render(request, 'product.html', context)

def update_product(request, id):
    queryset = Product.objects.get(id=id)

    if request.method == 'POST':
        data = request.POST

        name = data.get('name')
        description = data.get('description')
        category = data.get('category')
        price = data.get('price')
        bestSeller = request.POST.get('bestSeller', False) == 'on'
        image = request.FILES.get('image')

        queryset.name = name
        queryset.description = description
        queryset.category = category
        queryset.price = price
        queryset.bestSeller = bestSeller

        
        if image:
            queryset.image = image
        if category:
            queryset.category = category
        if bestSeller:
            queryset.bestSeller = bestSeller

        queryset.save() 
        messages.success(request, f'Product "{name}" edited successfully!!')
        return redirect("/dashboard/product")
    
    context = {'product': queryset}
    return render(request, 'update.html', context)

def delete_product(request, id):
    queryset = Product.objects.get(id=id) 
    queryset.delete()
    messages.success(request, f'Product deleted successfully!!')
    return redirect('/dashboard/product/')
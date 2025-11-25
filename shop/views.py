from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.conf import settings

import os

from .models import Product, Category, Order, OrderItem
from .cart import Cart
from .utils import generate_invoice_pdf


# ---------------------- Product Views ---------------------- #

def product_list(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()

    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    return render(request, 'shop/product_list.html', {
        'products': products,
        'categories': categories
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'shop/product_detail.html', {'product': product})


# ---------------------- Cart Views ---------------------- #

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'shop/cart_detail.html', {
        'cart': cart,
        'total': cart.get_total_price(),
    })


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, available=True)
    cart.add(product=product)
    messages.success(request, f"{product.name} added to cart!")
    return redirect('cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"{product.name} removed from cart.")
    return redirect('cart_detail')


# ---------------------- Checkout View ---------------------- #

@login_required
def checkout(request):
    cart = Cart(request)

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            total_price=cart.get_total_price(),
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price'],
            )

        file_name = generate_invoice_pdf(order)  # Generate invoice PDF
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        cart.clear()
        messages.success(request, "Order placed successfully!")

        return FileResponse(open(file_path, 'rb'),
                            as_attachment=True,
                            filename=file_name)

    return render(request, 'shop/checkout.html', {'cart': cart})


# ---------------------- Authentication Views ---------------------- #

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'shop/signup.html', {'form': form})


# ---------------------- User Orders View ---------------------- #

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/my_orders.html', {'orders': orders})


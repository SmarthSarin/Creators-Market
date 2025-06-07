import os
import json
import uuid
import razorpay
from weasyprint import CSS, HTML
from products.models import *
from django.urls import reverse
from django.conf import settings # Ensure this import is at the top
from django.contrib import messages
from django.http import JsonResponse
from home.models import ShippingAddress
from django.contrib.auth.models import User
from django.template.loader import get_template
from accounts.models import Profile, Cart, CartItem, Order, OrderItem
from base.emails import send_account_activation_email
from django.views.decorators.http import require_POST
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import redirect, render, get_object_or_404
from accounts.forms import UserUpdateForm, UserProfileForm, ShippingAddressForm, CustomPasswordChangeForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def login_page(request):
    next_url = request.GET.get('next') # Get the next URL from the query parameter
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username=username)

        if not user_obj.exists():
            messages.warning(request, 'Account not found!')
            return HttpResponseRedirect(request.path_info)

        if not user_obj[0].profile.is_email_verified:
            messages.error(request, 'Account not verified!')
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username=username, password=password)
        if user_obj:
            login(request, user_obj)
            messages.success(request, 'Login Successfull.')

            # Check if the next URL is safe
            if url_has_allowed_host_and_scheme(url=next_url, allowed_hosts=request.get_host()):
                return redirect(next_url)
            else:
                return redirect('index')

        messages.warning(request, 'Invalid credentials.')
        return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/login.html')


def register_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username=username, email=email)

        if user_obj.exists():
            messages.info(request, 'Username or email already exists!')
            return HttpResponseRedirect(request.path_info)

        user_obj = User.objects.create(
            username=username, first_name=first_name, last_name=last_name, email=email)
        user_obj.set_password(password)
        user_obj.save()

        profile = Profile.objects.get(user=user_obj)
        profile.email_token = str(uuid.uuid4())
        profile.save()

        send_account_activation_email(email, profile.email_token)
        messages.success(request, "An email has been sent to your mail.")
        return HttpResponseRedirect(request.path_info)

    return render(request, 'accounts/register.html')


@login_required
def user_logout(request):
    logout(request)
    messages.warning(request, "Logged Out Successfully!")
    return redirect('index')


def activate_email_account(request, email_token):
    try:
        user = Profile.objects.get(email_token=email_token)
        user.is_email_verified = True
        user.save()
        messages.success(request, 'Account verification successful.')
        return redirect('login')
    except Exception as e:
        return HttpResponse('Invalid email token.')


@login_required
def add_to_cart(request, uid):
    try:
        variant = request.GET.get('size')
        if not variant:
            messages.warning(request, 'Please select a size variant!')
            return redirect(request.META.get('HTTP_REFERER'))

        product = get_object_or_404(Product, uid=uid)
        cart, _ = Cart.objects.get_or_create(user=request.user, is_paid=False)
        size_variant = get_object_or_404(SizeVariant, size_name=variant)

        # Check stock availability
        stock = ProductStock.objects.filter(product=product, size_variant=size_variant).first()
        if not stock or stock.quantity <= 0:
            messages.error(request, 'Sorry, this item is out of stock!')
            return redirect(request.META.get('HTTP_REFERER'))

        # Check if adding one more would exceed stock
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, size_variant=size_variant)
        
        if not created:
            if cart_item.quantity + 1 > stock.quantity:
                messages.error(request, f'Sorry, only {stock.quantity} items available in stock!')
                return redirect(request.META.get('HTTP_REFERER'))
            cart_item.quantity += 1
            cart_item.save()

        # Check for low stock warning
        if stock.is_low_stock():
            messages.warning(request, f'Warning: Only {stock.quantity} items left in stock!')

        messages.success(request, 'Item added to cart successfully.')

    except Exception as e:
        messages.error(request, 'Error adding item to cart.', str(e))

    return redirect(reverse('cart'))


@login_required
def cart(request):
    cart_obj = None
    payment = None
    user = request.user

    try:
        cart_obj = Cart.objects.get(is_paid=False, user=user)

    except Exception as e:
        messages.warning(request, "Your cart is empty. Please add a product to cart.", str(e))
        return redirect(reverse('index'))

    if request.method == 'POST':
        coupon = request.POST.get('coupon')
        coupon_obj = Coupon.objects.filter(coupon_code__exact=coupon).first()

        if not coupon_obj:
            messages.warning(request, 'Invalid coupon code.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if cart_obj and cart_obj.coupon:
            messages.warning(request, 'Coupon already exists.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if coupon_obj and coupon_obj.is_expired:
            messages.warning(request, 'Coupon code expired.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if cart_obj and coupon_obj and cart_obj.get_cart_total() < coupon_obj.minimum_amount:
            messages.warning(
                request, f'Amount should be greater than {coupon_obj.minimum_amount}')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if cart_obj and coupon_obj:
            cart_obj.coupon = coupon_obj
            cart_obj.save()
            messages.success(request, 'Coupon applied successfully.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if cart_obj:
        cart_total_in_paise = int(cart_obj.get_cart_total_price_after_coupon() * 100)

        if cart_total_in_paise < 100:
            messages.warning(
                request, 'Total amount in cart is less than the minimum required amount (1.00 INR). Please add a product to the cart.')
            return redirect('index')

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
        payment = client.order.create(
            {'amount': cart_total_in_paise, 'currency': 'INR', 'payment_capture': 1})
        cart_obj.razorpay_order_id = payment['id']
        cart_obj.save()

    context = {'cart': cart_obj, 'payment': payment, 'quantity_range': range(1, 6), 'razorpay_key_id': settings.RAZORPAY_KEY_ID}
    return render(request, 'accounts/cart.html', context)


@require_POST
@login_required
def update_cart_item(request):
    try:
        data = json.loads(request.body)
        cart_item_id = data.get("cart_item_id")
        quantity = int(data.get("quantity"))

        cart_item = CartItem.objects.get(uid=cart_item_id, cart__user=request.user, cart__is_paid=False)
        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


def remove_cart(request, uid):
    try:
        cart_item = get_object_or_404(CartItem, uid=uid)
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')

    except Exception as e:
        print(e)
        messages.warning(request, 'Error removing item from cart.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def remove_coupon(request, cart_id):
    cart = Cart.objects.get(uid=cart_id)
    cart.coupon = None
    cart.save()

    messages.success(request, 'Coupon Removed.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Payment success view
def success(request):
    order_id = request.GET.get('order_id')
    cart = get_object_or_404(Cart, razorpay_order_id=order_id)

    # Mark the cart as paid
    cart.is_paid = True
    cart.save()

    # Create the order after payment is confirmed
    order = create_order(cart)

    # Generate PDF invoice
    order_items = order.order_items.all()
    context = {
        'order': order,
        'order_items': order_items,
    }
    pdf = render_to_pdf('accounts/order_pdf_generate.html', context)

    # Send thank you email with PDF attachment
    subject = f"Thank you for your order #{order.order_id}"
    message = f"""
    Dear {order.user.get_full_name() or order.user.username},

    Thank you for your purchase! Your order has been successfully placed.

    Order Details:
    Order ID: {order.order_id}
    Total Amount: ₹{order.grand_total}
    Payment Status: {order.payment_status}
    Payment Mode: {order.payment_mode}

    Please find your invoice attached to this email.

    Thank you for shopping with us!

    Best regards,
    Creator's Market Team
    """

    try:
        # Create email message with PDF attachment
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.application import MIMEApplication
        from django.core.mail import EmailMessage

        email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
        )
        
        # Attach the PDF
        email.attach(f'invoice_{order.order_id}.pdf', pdf.getvalue(), 'application/pdf')
        email.send(fail_silently=False)
        
        print(f"Thank you email sent to {order.user.email} for order {order.order_id}")
    except Exception as e:
        print(f"Error sending thank you email: {e}")

    # Clear the cart after successful payment
    cart.cart_items.all().delete()

    context = {'order_id': order_id, 'order': order}
    return render(request, 'payment_success/payment_success.html', context)


# HTML to PDF Conversion
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)

    static_dir = os.path.join(settings.BASE_DIR, "public/media")
    css_files = [
        os.path.join(static_dir, 'css', 'bootstrap.css'),
        os.path.join(static_dir, 'css', 'responsive.css'),
        os.path.join(static_dir, 'css', 'ui.css'),
    ]
    css_objects = [CSS(filename=css_file) for css_file in css_files]
    pdf_file = HTML(string=html).write_pdf(stylesheets=css_objects)

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{context_dict["order"].order_id}.pdf"'
    return response


def download_invoice(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    order_items = order.order_items.all()

    context = {
        'order': order,
        'order_items': order_items,
    }

    pdf = render_to_pdf('accounts/order_pdf_generate.html', context)
    if pdf:
        return pdf
    return HttpResponse("Error generating PDF", status=400)


@login_required
def profile_view(request, username):
    user_name = get_object_or_404(User, username=username)
    user = request.user
    profile = user.profile

    user_form = UserUpdateForm(instance=user)
    profile_form = UserProfileForm(instance=profile)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    context = {
        'user_name': user_name,
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'accounts/profile.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, 'Please correct the error below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def update_shipping_address(request):
    shipping_address = ShippingAddress.objects.filter(
        user=request.user, current_address=True).first()

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=shipping_address)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.current_address = True
            shipping_address.save()

            # Update the user's profile with the new shipping address
            profile = request.user.profile
            profile.shipping_address = shipping_address
            profile.save()

            messages.success(request, "The Address Has Been Successfully Saved/Updated!")
            return redirect('shipping-address')
        else:
            form = ShippingAddressForm(request.POST, instance=shipping_address)
    else:
        form = ShippingAddressForm(instance=shipping_address)

    return render(request, 'accounts/shipping_address_form.html', {'form': form})


# Order history view
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'accounts/order_history.html', {'orders': orders})


# Create an order view
def create_order(cart):
    # Format shipping address as a string
    shipping_address_str = "Not Provided"
    if cart.user.profile.shipping_address:
        addr = cart.user.profile.shipping_address
        shipping_address_str = f"{addr.first_name} {addr.last_name}\n{addr.street} {addr.street_number}\n{addr.city}, {addr.country}\n{addr.zip_code}\nPhone: {addr.phone}"

    order, created = Order.objects.get_or_create(
        user=cart.user,
        order_id=cart.razorpay_order_id,
        payment_status="Paid",
        shipping_address=shipping_address_str,
        payment_mode="Razorpay",
        order_total_price=cart.get_cart_total(),
        coupon=cart.coupon,
        grand_total=cart.get_cart_total_price_after_coupon(),
    )

    # Create OrderItem instances for each item in the cart
    cart_items = CartItem.objects.filter(cart=cart)
    for cart_item in cart_items:
        order_item, item_created = OrderItem.objects.get_or_create( 
            order=order,
            product=cart_item.product,
            size_variant=cart_item.size_variant, # Size is on the OrderItem model
            color_variant=cart_item.color_variant, # Color is on the OrderItem model
            quantity=cart_item.quantity,
            defaults={'product_price': cart_item.get_product_price()} 
        )
        
        if item_created or not order_item.product_price:
             order_item.product_price = cart_item.get_product_price()
             order_item.save()

        # --- Seller Notification Logic using settings.SELLER_EMAIL --- 
        seller_email_address = settings.SELLER_EMAIL
        if seller_email_address:
            # Prepare details for the email
            purchaser_name = order.user.get_full_name() or order.user.username
            shipping_address_details = order.shipping_address  # Use the formatted address string directly
            
            product_size = order_item.size_variant.size_name if order_item.size_variant else "N/A"
            product_color = order_item.color_variant.color_name if order_item.color_variant else "N/A"

            subject = f"New Order Received for {order_item.product.product_name}"
            message = (
                f"Hello,\n\n"
                f"A new order has been placed for your product: {order_item.product.product_name}.\n\n"
                f"Order Details:\n"
                f"  Order ID: {order.order_id}\n"
                f"  Product Name: {order_item.product.product_name}\n"
                f"  Quantity: {order_item.quantity}\n"
                f"  Size: {product_size}\n"
                f"  Color: {product_color}\n"
                f"  Price per item: {order_item.product_price}\n"
                f"  Total for this item: {order_item.get_total_price()}\n\n"
                f"Purchased By:\n"
                f"  Name: {purchaser_name}\n"
                f"  Email: {order.user.email}\n\n"
                f"Shipping Address:\n{shipping_address_details}\n\n"
                f"Thank you."
            )
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL, 
                    [seller_email_address],
                    fail_silently=False, 
                )
                print(f"Seller notification email sent to {seller_email_address} for product {order_item.product.product_name}")
            except Exception as e:
                print(f"Error sending seller notification email: {e}")
        else:
            print(f"SELLER_EMAIL not configured in settings. Skipping notification for product {order_item.product.product_name}.")
        # --- End Seller Notification Logic ---

    return order


# Order Details view
@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    context = {
        'order': order,
        'order_items': order_items,
        'order_total_price': sum(item.get_total_price() for item in order_items),
        'coupon_discount': order.coupon.discount_amount if order.coupon else 0,
        'grand_total': order.get_order_total_price()
    }
    return render(request, 'accounts/order_details.html', context)


# Delete user account feature
@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('index')

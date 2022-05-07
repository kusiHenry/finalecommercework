from django.shortcuts import render, redirect
from django.http import JsonResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.paginator import Paginator, EmptyPage
import json
import datetime

from store.decorators import unauthenticated_user, allowed_users
from .models import *
from .utils import cartData, guestOrder
from .forms import CreateUserForm
from .filters import ProductFilter



@unauthenticated_user
def registerPage(request):

	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			Customer.objects.create(user=user, name=user.username, email=user.email)
			username = form.cleaned_data.get('username')

			group = Group.objects.get(name='customer')
			user.groups.add(group)
			messages.success(request, 'Account was created for ' + username)

			return redirect('login')

	context = {'form':form}
	return render(request, 'accounts/register.html', context)

@login_required(login_url='login')
def store(request):
	
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	
	products = Product.objects.all()
	

	myFilter = ProductFilter(request.GET, queryset=products)
	products = myFilter.qs

	pagin =Paginator(products, 30)
	page_num = request.GET.get('page', 1)
	page = pagin.get_page(page_num)

	context = {'products':products, 'cartItems':cartItems, 'myFilter':myFilter, 'page':page}
	return render(request, 'store/store.html', context )

def products(request):
	products = Product.objects.all()
	


	return render(request, 'store/store.html', {'products':products})


def dashboard(request):
	data = cartData(request)

	cartItems = data['cartItems']
	
	products = Product.objects.all()
	myFilter = ProductFilter(request.GET, queryset=products)
	products = myFilter.qs

	pagin =Paginator(products, 30)
	page_num = request.GET.get('page', 1)
	page = pagin.get_page(page_num)

	context = {'products':products, 'cartItems':cartItems, 'myFilter':myFilter, 'page':page}
	return render(request, 'store/dashboard.html', context)

@unauthenticated_user
def loginPage(request):

	if request.method == 'POST':
		username = request.POST.get('username')
		password =request.POST.get('password')

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect('store')
		else:
			messages.info(request, 'Username OR password is incorrect')

	context = {}
	return render(request, 'accounts/login.html', context)

def logoutUser(request):
	logout(request)
	return redirect('dashboard')

@login_required(login_url='login')
def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

@login_required(login_url='login')
def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)


#from django.views.decorators.csrf import csrf_exempt

#csrf_exempt
@login_required(login_url='login')
def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)

# def handle_not_found(request, exception):
# 	return render(request, 'store/not_found.html')
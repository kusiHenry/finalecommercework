from django.urls import path
from django.conf.urls import handler404

from . import views

urlpatterns = [
	#Leave as empty string for base url
	path('', views.dashboard, name="dashboard"),
	path('store/', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),

	path('register/', views.registerPage, name="register"),
	path('login/', views.loginPage, name="login"),  
	path('logout/', views.logoutUser, name="logout"),
	

	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),

]

# handler404 = "views.handle_not_found"
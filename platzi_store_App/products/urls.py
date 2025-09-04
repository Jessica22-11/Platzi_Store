from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path("", views.products_home, name="products_home"),
    path('list/',views.list_products, name="list_products"),
    path('create/',views.create_product,name="create_product"),
    path("search/", views.search_products, name="search_products"),
    path("<int:product_id>/", views.product_detail, name="product_detail"),
]

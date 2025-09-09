from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path("", views.home, name="home"),
    path("list/",views.list_products, name="list_products"),
    path("category/<int:category_id>/", views.products_by_category, name="products_by_category"),
    path("create/",views.create_product,name="create_product"),
    path("update/<int:product_id>/", views.update_product, name="update_product"),
    path("delete/<int:product_id>/", views.delete_product, name="delete_product"),
    path("search/", views.search_products, name="search_products"),
    path("<int:product_id>/", views.product_detail, name="product_detail"),
]

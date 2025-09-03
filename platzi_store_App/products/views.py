from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from .forms import ProductForm

base_url = "https://api.escuelajs.co/api/v1/products"

def products_home(request):
    return render(request, "base.html")

def list_products(request):
    try:
        response = requests.get(f"{base_url}", timeout=10)
        if response.status_code == 200:
            products = response.json()
            return render(request, "list_products.html", {"products": products})

        else:
            return render(request, "products/list_products.html", {
                "error": f"Error en la API: {response.status_code}"
            })
    except requests.exceptions.Timeout:
        return render(request, "list_products.html", {
            "error": "⏱ Tiempo de espera agotado."
        })
    except requests.exceptions.ConnectionError:
        return render(request, "list_products.html", {
            "error": "❌ Error de conexión."
        })
    except Exception as e:
        return render(request, "list_products.html", {
            "error": f"⚠️ Error inesperado: {str(e)}"
        })

@csrf_exempt
def create_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            new_product = {
                "title": form.cleaned_data["title"],
                "price": float(form.cleaned_data["price"]),
                "description": form.cleaned_data["description"],
                "categoryId": form.cleaned_data["categoryId"],
                "images": [form.cleaned_data["image_url"]]
            }

            response = requests.post(base_url, json=new_product, timeout=10)

            if response.status_code == 201:
                product = response.json()
                return render(request, "create_product.html", {
                    "form": ProductForm(),
                    "success": f"✅ Producto creado exitosamente. ID: {product['id']} - Título: {product['title']}"
                })
            else:
                return render(request, "create_product.html", {
                    "form": form,
                    "error": f"Error en la API: {response.status_code} - {response.text}"
                })
    else:
        form = ProductForm()

    return render(request, "create_product.html", {"form": form})


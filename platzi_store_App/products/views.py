from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from .forms import ProductForm

base_url = "https://api.escuelajs.co/api/v1/products"

def home(request):
    return render(request, "home.html")


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
                messages.success(
                    request,
                    f"✅ Producto creado exitosamente. ID: {product['id']} - Título: {product['title']}"
                )
                return redirect("products:list_products")
            else:
                messages.error(
                    request,
                    f"Error en la API: {response.status_code} - {response.text}"
                )
    else:
        form = ProductForm()

    return render(request, "create_product.html", {"form": form})

@csrf_exempt
def update_product(request, product_id):
    response = requests.get(f"{base_url}/{product_id}")
    if response.status_code != 200:
        return render(request, "update_product.html", {"error": "❌ Producto no encontrado."})

    product_data = response.json()

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            updated_product = {
                "title": form.cleaned_data["title"],
                "price": float(form.cleaned_data["price"]),
                "description": form.cleaned_data["description"],
                "categoryId": form.cleaned_data["categoryId"],
                "images": [form.cleaned_data["image_url"]],
            }
            put_response = requests.put(f"{base_url}/{product_id}", json=updated_product)
            if put_response.status_code == 200:
                # ✅ Mensaje de éxito antes del redirect
                messages.success(request, f"✅ Producto editado exitosamente. ID: {product_id}")
                return redirect("products:list_products")
            else:
                return render(request, "update_product.html", {
                    "form": form,
                    "error": f"❌ Error al actualizar: {put_response.status_code}"
                })
    else:
        form = ProductForm(initial={
            "title": product_data["title"],
            "price": product_data["price"],
            "description": product_data["description"],
            "categoryId": product_data["category"]["id"],
            "image_url": product_data["images"][0] if product_data["images"] else "",
        })
    return render(request, "update_product.html", {"form": form, "product": product_data})

@csrf_exempt
def delete_product(request, product_id):
    if request.method == "POST":
        url = f"https://api.escuelajs.co/api/v1/products/{product_id}"
        response = requests.delete(url)

        if response.status_code == 200 or response.status_code == 204:
            messages.success(request, "✅ Producto eliminado correctamente.")
        else:
            messages.error(request, "⚠️ No se pudo eliminar el producto.")

    return redirect("products:list_products")

def search_products(request):
    query = request.GET.get("q", "").strip()
    results = []
    error = None

    if query:
        try:
            if query.isdigit():
                response = requests.get(f"{base_url}/{query}", timeout=10)
                if response.status_code == 200:
                    product = response.json()
                    results = [product] 
                elif response.status_code == 404:
                    error = "❌ No se encontró ningún producto con ese ID."
                else:
                    error = f"⚠️ Error en la API: {response.status_code}"
        except requests.exceptions.Timeout:
            error = "⏱ Tiempo de espera agotado."
        except requests.exceptions.ConnectionError:
            error = "❌ Error de conexión."
        except Exception as e:
            error = f"⚠️ Error inesperado: {str(e)}"

    return render(request, "search_results.html", {
        "query": query,
        "results": results,
        "error": error,
    })

def product_detail(request, product_id):
    try:
        response = requests.get(f"{base_url}/{product_id}", timeout=10)
        if response.status_code == 200:
            product = response.json()
            return render(request, "product_detail.html", {"product": product})
        elif response.status_code == 404:
            return render(request, "product_detail.html", {
                "error": "❌ Producto no encontrado."
            })
        else:
            return render(request, "product_detail.html", {
                "error": f"⚠️ Error en la API: {response.status_code}"
            })

    except requests.exceptions.RequestException:   
        return render(request, "product_detail.html", {
            "error": "❌ Error de conexión con la API."
        })

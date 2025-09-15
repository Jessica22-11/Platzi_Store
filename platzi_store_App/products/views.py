import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from .forms import ProductForm

base_url = "https://api.escuelajs.co/api/v1/products"
categories_url = "https://api.escuelajs.co/api/v1/categories"

import requests
from django.shortcuts import render

def home(request):
    # API de categorías
    url_categories = "https://api.escuelajs.co/api/v1/categories"
    categories = []
    try:
        response = requests.get(url_categories)
        if response.status_code == 200:
            categories = response.json()
    except Exception as e:
        print("Error cargando categorías:", e)

    # API de productos destacados (ejemplo: primeros 6)
    url_products = "https://api.escuelajs.co/api/v1/products"
    products = []
    try:
        response = requests.get(url_products)
        if response.status_code == 200:
            products = response.json()[:6]  # solo los primeros 6
    except Exception as e:
        print("Error cargando productos:", e)

    return render(request, "home.html", {
        "categories": categories,
        "products": products
    })


@login_required(login_url='accounts:login')
def list_products(request):
    try:
        response = requests.get(f"{base_url}", timeout=10)
        if response.status_code == 200:
            products = response.json()
            return render(request, "list_products.html", {"products": products})

        else:
            return render(request, "list_products.html", {
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

@login_required(login_url='accounts:login')
def create_product(request):
    # 1. Pedir las categorías a la API
    try:
        response = requests.get(categories_url, timeout=10)
        response.raise_for_status()
        categories_data = response.json()
        categories = [(cat["id"], cat["name"]) for cat in categories_data]  # (id, nombre)
    except Exception as e:
        categories = []
        messages.error(request, f"⚠️ No se pudieron cargar categorías: {e}")

    # 2. Instanciar el formulario con categorías dinámicas
    if request.method == "POST":
        form = ProductForm(request.POST)
        form.fields["categoryId"].choices = categories  # 👈 aquí se asignan
        if form.is_valid():
            new_product = {
                "title": form.cleaned_data["title"],
                "price": float(form.cleaned_data["price"]),
                "description": form.cleaned_data["description"],
                "categoryId": int(form.cleaned_data["categoryId"]),
                "images": [form.cleaned_data["image_url"]],
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
        form.fields["categoryId"].choices = categories  # 👈 también en GET

    return render(request, "create_product.html", {"form": form})

@login_required(login_url='accounts:login')
def update_product(request, product_id):
    # 1. Obtener producto actual
    response = requests.get(f"{base_url}/{product_id}")
    if response.status_code != 200:
        return render(request, "update_product.html", {"error": "❌ Producto no encontrado."})

    product_data = response.json()

    # 2. Obtener categorías de la API
    try:
        categories_response = requests.get(categories_url, timeout=10)
        categories_response.raise_for_status()
        categories_data = categories_response.json()
        categories = [(cat["id"], cat["name"]) for cat in categories_data]  # (id, nombre)
    except Exception as e:
        categories = []
        messages.error(request, f"⚠️ No se pudieron cargar categorías: {e}")

    if request.method == "POST":
        form = ProductForm(request.POST)
        form.fields["categoryId"].choices = categories  # 👈 asignar categorías dinámicas

        if form.is_valid():
            updated_product = {
                "title": form.cleaned_data["title"],
                "price": float(form.cleaned_data["price"]),
                "description": form.cleaned_data["description"],
                "categoryId": int(form.cleaned_data["categoryId"]),
                "images": [form.cleaned_data["image_url"]],
            }

            put_response = requests.put(f"{base_url}/{product_id}", json=updated_product)
            if put_response.status_code == 200:
                messages.success(request, f"✅ Producto editado exitosamente. ID: {product_id}")
                return redirect("products:list_products")
            else:
                return render(request, "update_product.html", {
                    "form": form,
                    "error": f"❌ Error al actualizar: {put_response.status_code}"
                })
    else:
        # 3. Prellenar formulario con datos del producto
        form = ProductForm(initial={
            "title": product_data["title"],
            "price": product_data["price"],
            "description": product_data["description"],
            "categoryId": product_data["category"]["id"],  # 👈 id actual
            "image_url": product_data["images"][0] if product_data["images"] else "",
        })
        form.fields["categoryId"].choices = categories  # 👈 cargar categorías también en GET

    return render(request, "update_product.html", {"form": form, "product": product_data})


@login_required(login_url='accounts:login')
def delete_product(request, product_id):
    if request.method == "POST":
        url = f"https://api.escuelajs.co/api/v1/products/{product_id}"
        response = requests.delete(url)

        if response.status_code == 200 or response.status_code == 204:
            messages.success(request, "✅ Producto eliminado correctamente.")
        else:
            messages.error(request, "⚠️ No se pudo eliminar el producto.")

    return redirect("products:list_products")

def products_by_category(request, category_id):
    url = f"https://api.escuelajs.co/api/v1/categories/{category_id}/products"
    products = []
    try:
        response = requests.get(url)
        if response.status_code == 200:
            products = response.json()
    except Exception as e:
        print("Error cargando productos por categoría:", e)

    return render(request, "list_products.html", {"products": products})

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
                    results = [product]  # lo convertimos en lista para iterar en la template
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

    except requests.exceptions.RequestException:   # 👈 aquí va `requests` (la librería)
        return render(request, "product_detail.html", {
            "error": "❌ Error de conexión con la API."
        })
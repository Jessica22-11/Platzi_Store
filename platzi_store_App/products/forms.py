from django import forms

class ProductForm(forms.Form):
    title = forms.CharField(
        label="Nombre del producto",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    price = forms.DecimalField(
        label="Precio",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label="Descripcion",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows':3})
    )
    categoryId = forms.ChoiceField(
        label="Categoría",
        choices=[],  # 👈 se llenará dinámicamente en la vista
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    image_url = forms.URLField(
        label= "URL de la imagen",
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
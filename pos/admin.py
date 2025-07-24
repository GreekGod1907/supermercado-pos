# pos/admin.py
from django.contrib import admin
from .models import Producto, Venta, DetalleVenta, Inventario

# Esta clase permite que editemos el Inventario DENTRO de la página del Producto
class InventarioInline(admin.StackedInline):
    model = Inventario
    can_delete = False # No permitir borrar el inventario desde el producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Muestra más campos en la lista de productos
    list_display = ('nombre', 'codigo_barra') 
    # Añade un campo de búsqueda
    search_fields = ('nombre', 'codigo_barra')
    # Añade el formulario de Inventario a la página de Producto
    inlines = [InventarioInline]

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    # Muestra los detalles de la venta en modo de solo lectura
    list_display = ('id', 'fecha_venta', 'total')
    readonly_fields = ('fecha_venta', 'total')

# Registramos los otros modelos de forma simple
admin.site.register(DetalleVenta)
admin.site.register(Inventario)
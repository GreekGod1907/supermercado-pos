# pos/migrations/0002_poblar_productos.py
from django.db import migrations

def poblar_datos(apps, schema_editor):
    Producto = apps.get_model('pos', 'Producto')
    Inventario = apps.get_model('pos', 'Inventario')

    productos_data = [
        {'nombre': 'Leche Entera 1L', 'codigo_barra': '101', 'precio': 3500.00, 'cantidad': 50},
        {'nombre': 'Pan Tajado Bimbo', 'codigo_barra': '102', 'precio': 4200.00, 'cantidad': 30},
        {'nombre': 'Huevos x12 AA', 'codigo_barra': '103', 'precio': 8000.00, 'cantidad': 100},
        # ... puedes agregar más si quieres
    ]

    for data in productos_data:
        producto, created = Producto.objects.get_or_create(
            codigo_barra=data['codigo_barra'],
            defaults={'nombre': data['nombre']}
        )
        Inventario.objects.create(
            producto=producto,
            cantidad=data['cantidad'],
            precio_venta=data['precio']
        )

class Migration(migrations.Migration):
    dependencies = [
        ('pos', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(poblar_datos, reverse_code=migrations.RunPython.noop),
    ]
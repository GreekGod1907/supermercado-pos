import json
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Producto, Venta, DetalleVenta, Inventario # <-- Asegúrate de importar Inventario
from django.contrib.auth.decorators import login_required

def pos_view(request):
    return render(request, 'pos/pos.html')

@login_required
def registrar_productos_view(request):
    return render(request, 'pos/registrar_productos.html')

# VISTA DE API ACTUALIZADA para buscar productos
def buscar_producto_api(request):
    codigo_barras = request.GET.get('codigo_barra', None)
    if not codigo_barras:
        return JsonResponse({'error': 'Código de barra no proporcionado'}, status=400)

    try:
        # Buscamos en el Inventario y traemos el Producto relacionado en una sola consulta
        inventario_item = Inventario.objects.select_related('producto').get(producto__codigo_barra=codigo_barras)

        # Extraemos los datos del producto y del inventario
        producto = inventario_item.producto

        data = {
            'nombre': producto.nombre,
            'precio': str(inventario_item.precio_venta) # <-- Obtenemos el precio del Inventario
        }
        return JsonResponse(data)
    except Inventario.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado en el inventario'}, status=404)


# VISTA DE API ACTUALIZADA para finalizar la venta y descontar stock
@csrf_exempt
@transaction.atomic
def finalizar_venta_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            total = data.get('total', 0)

            if not items:
                return JsonResponse({'error': 'No hay productos en la venta'}, status=400)

            # 1. Crear el objeto Venta
            venta = Venta.objects.create(total=total)

            # 2. Procesar cada item, descontar inventario y crear DetalleVenta
            for item in items:
                producto = Producto.objects.get(codigo_barra=item['codigo_barra'])
                
                try:
                    inventario = Inventario.objects.get(producto=producto)
                except Inventario.DoesNotExist:
                    # Esto no debería pasar si buscar_producto_api funcionó, pero es una buena validación
                    return JsonResponse({'error': f'Inventario no encontrado para {producto.nombre}'}, status=400)

                # Verificamos si hay stock suficiente
                if inventario.cantidad < item['cantidad']:
                    # Si no hay stock, la transacción completa se revierte gracias a @transaction.atomic
                    return JsonResponse({'error': f'Stock insuficiente para {producto.nombre}'}, status=400)
                
                # Descontamos el stock
                inventario.cantidad -= item['cantidad']
                inventario.save()

                # Creamos el detalle de la venta
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio']
                )
            
            # 3. Devolver una respuesta exitosa
            return JsonResponse({'success': True, 'venta_id': venta.id})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

#VISTA RECIBO
def recibo_venta_view(request, venta_id):
    try:
        venta = Venta.objects.get(id=venta_id)
        detalles = DetalleVenta.objects.filter(venta=venta)
        contexto = {
            'venta': venta,
            'detalles': detalles,
        }
        return render(request, 'pos/recibo.html', contexto)
    except Venta.DoesNotExist:
        return JsonResponse({'error': 'Venta no encontrada'}, status=404)
    
@csrf_exempt
@transaction.atomic
def registrar_lote_api(request):
    if request.method == 'POST':
        try:
            lote = json.loads(request.body)
            for item in lote:
                producto, created = Producto.objects.update_or_create(
                    codigo_barra=item['codigo_barra'],
                    defaults={'nombre': item['nombre']}
                )

                inventario, inv_created = Inventario.objects.update_or_create(
                    producto=producto,
                    defaults={
                        'cantidad': int(item['cantidad']),
                        'precio_venta': float(item['precio'])
                    }
                )
            return JsonResponse({'success': True, 'productos_procesados': len(lote)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)
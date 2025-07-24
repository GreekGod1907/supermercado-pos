import json
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Producto, Venta, DetalleVenta, Inventario
from django.contrib.auth.decorators import login_required

def pos_view(request):
    return render(request, 'pos/pos.html')

@login_required
def registrar_productos_view(request):
    return render(request, 'pos/registrar_productos.html')

# VISTA DE API para buscar productos
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
            'precio': str(inventario_item.precio_venta)
        }
        return JsonResponse(data)
    except Inventario.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado en el inventario'}, status=404)


# VISTA DE API para finalizar la venta y descontar stock
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
                    return JsonResponse({'error': f'Inventario no encontrado para {producto.nombre}'}, status=400)

                # Verificamos si hay stock suficiente
                if inventario.cantidad < item['cantidad']:
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

# VISTA RECIBO
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

# VISTA DE API CORREGIDA para registrar lote - SUMA al inventario existente
@csrf_exempt
@transaction.atomic
def registrar_lote_api(request):
    if request.method == 'POST':
        try:
            lote = json.loads(request.body)
            productos_procesados = 0
            
            for item in lote:
                # 1. Crear o actualizar el producto
                producto, created = Producto.objects.update_or_create(
                    codigo_barra=item['codigo_barra'],
                    defaults={'nombre': item['nombre']}
                )

                # 2. Manejar el inventario - SUMAR en lugar de reemplazar
                try:
                    # Si ya existe el inventario, lo obtenemos y sumamos
                    inventario = Inventario.objects.get(producto=producto)
                    inventario.cantidad += int(item['cantidad'])  # SUMA la cantidad
                    inventario.precio_venta = float(item['precio'])  # Actualiza el precio
                    inventario.save()
                    
                except Inventario.DoesNotExist:
                    # Si no existe, lo creamos nuevo
                    inventario = Inventario.objects.create(
                        producto=producto,
                        cantidad=int(item['cantidad']),
                        precio_venta=float(item['precio'])
                    )
                
                productos_procesados += 1
            
            return JsonResponse({
                'success': True, 
                'productos_procesados': productos_procesados,
                'message': f'Se han procesado {productos_procesados} productos. Las cantidades se sumaron al inventario existente.'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)
# pos/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # La URL para la página principal del POS
    path('', views.pos_view, name='pos_view'),

    # La URL para la API que busca productos
    path('api/buscar-producto/', views.buscar_producto_api, name='buscar_producto_api'),

    # La URL para finalizar venta
    path('api/finalizar-venta/', views.finalizar_venta_api, name='finalizar_venta_api'),
    
    # URL para el recibo de venta
    path('recibo/<int:venta_id>/', views.recibo_venta_view, name='recibo_venta'),

    # URL para registrar lote de productos
    path('api/registrar-lote/', views.registrar_lote_api, name='registrar_lote_api'),

    # URL para la página de registrar productos
    path('registrar-productos/', views.registrar_productos_view, name='registrar_productos'),
]
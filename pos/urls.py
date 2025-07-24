# pos/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # La URL para la página principal del POS
    path('', views.pos_view, name='pos_view'),

    # La URL para la API que busca productos
    path('api/buscar-producto/', views.buscar_producto_api, name='buscar_producto_api'),

    # AÑADE ESTA LÍNEA:
    path('api/finalizar-venta/', views.finalizar_venta_api, name='finalizar_venta_api'),
    #url recibo  venta
    path('recibo/<int:venta_id>/', views.recibo_venta_view, name='recibo_venta'),

    path('api/registrar-lote/', views.registrar_lote_api, name='registrar_lote_api'),

    path('registrar-productos/', views.registrar_productos_view, name='registrar_productos'),
]


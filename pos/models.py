# pos/models.py
from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    codigo_barra = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Inventario(models.Model):
    # Un producto solo puede tener una entrada en el inventario
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=0) # Usamos PositiveIntegerField para el stock
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} (Stock: {self.cantidad})"

# Los modelos Venta y DetalleVenta se quedan igual
class Venta(models.Model):
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Venta #{self.id} - {self.fecha_venta.strftime('%Y-%m-%d %H:%M:%S')}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT) # Se enlaza al producto general
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
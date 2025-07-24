import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from pos.models import Producto, Inventario

class Command(BaseCommand):
    help = 'Importa productos e inventario desde un archivo CSV especificado'

    def add_arguments(self, parser):
        # Argumento posicional para la ruta del archivo CSV
        parser.add_argument('csv_file_path', type=str, help='La ruta completa al archivo CSV a importar.')

    @transaction.atomic # Usamos una transacción para asegurar la integridad de los datos
    def handle(self, *args, **options):
        file_path = options['csv_file_path']
        self.stdout.write(self.style.SUCCESS(f'Iniciando importación desde "{file_path}"...'))

        try:
            with open(file_path, mode='r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                
                for row in reader:
                    # Crea o actualiza el Producto
                    producto, created = Producto.objects.update_or_create(
                        codigo_barra=row['codigo_barra'],
                        defaults={'nombre': row['nombre']}
                    )
                    
                    # Crea o actualiza su entrada en el Inventario
                    Inventario.objects.update_or_create(
                        producto=producto,
                        defaults={
                            'cantidad': int(row['cantidad']),
                            'precio_venta': float(row['precio'])
                        }
                    )

                    if created:
                        self.stdout.write(f'  - Creado producto: {producto.nombre}')
                    else:
                        self.stdout.write(f'  - Actualizado producto: {producto.nombre}')

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: El archivo "{file_path}" no fue encontrado.'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocurrió un error inesperado: {e}'))
            return

        self.stdout.write(self.style.SUCCESS('¡Importación completada con éxito!'))
# create_batch.py - VERSIÓN CORREGIDA Y FUNCIONAL
from django.core.management.base import BaseCommand
from django.core.management import call_command
from nfc_manager.models import NFCBatch, NFCItem
from nfc_manager.utils.nfc_generator import generate_secure_token, generate_activation_code, hash_activation_code
import csv
import os

class Command(BaseCommand):
    help = 'Crea un lote de soportes NFC (pulseras, pegatinas, etc)'
    
    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Nombre del lote')
        parser.add_argument('type', type=str, help='Tipo: pulsera, pegatina, tarjeta, llavero')
        parser.add_argument('quantity', type=int, help='Cantidad de unidades')
        parser.add_argument('--export', action='store_true', help='Exportar CSV')
    
    def handle(self, *args, **options):
        name = options['name']
        support_type = options['type']
        quantity = options['quantity']
        
        self.stdout.write(self.style.SUCCESS(f'\n🚀 Creando lote: {name}'))
        self.stdout.write(f'📦 Tipo: {support_type}')
        self.stdout.write(f'🔢 Cantidad: {quantity}\n')
        
        # 1. Crear el lote
        batch = NFCBatch.objects.create(
            name=name,
            support_type=support_type,
            quantity=quantity
        )
        
        self.stdout.write(f'✅ Lote #{batch.id} creado\n')
        self.stdout.write('🔄 Generando códigos seguros...')
        
        # 2. Generar items
        items_to_create = []
        codes_for_csv = []
        
        for i in range(quantity):
            token = generate_secure_token()
            plain_code = generate_activation_code()
            hashed_code = hash_activation_code(plain_code)
            
            item = NFCItem(
                batch=batch,
                public_token=token,
                activation_code_hash=hashed_code,
                status='inactive'
            )
            items_to_create.append(item)
            
            codes_for_csv.append({
                'token': token,
                'codigo': plain_code,
                'url': f'http://127.0.0.1:8000/t/{token}'
            })
            
            if (i + 1) % 100 == 0:
                self.stdout.write(f'   Generados {i + 1} de {quantity}...')
        
        # 3. Guardar en BD
        NFCItem.objects.bulk_create(items_to_create)
        self.stdout.write(self.style.SUCCESS(f'\n✨ {quantity} items creados\n'))
        
        # 4. Exportar CSV si se pide
        if options['export']:
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            filename = f'lote_{batch.id}_{name.replace(" ", "_")}.csv'
            filepath = os.path.join(desktop, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['TOKEN', 'URL_NFC', 'CODIGO_ACTIVACION', 'TIPO'])
                
                for item_data in codes_for_csv:
                    writer.writerow([
                        item_data['token'],
                        item_data['url'],
                        item_data['codigo'],
                        support_type
                    ])
            
            self.stdout.write(self.style.SUCCESS(f'📄 CSV: {filepath}'))
        
        # 5. Mostrar ejemplos
        if quantity > 0:
            self.stdout.write('\n🔍 EJEMPLOS (primeros 3):')
            for i, item in enumerate(codes_for_csv[:3]):
                self.stdout.write(f'\n   {i+1}. URL: {item["url"]}')
                self.stdout.write(f'      Código: {item["codigo"]}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ ¡LOTE COMPLETADO!\n'))
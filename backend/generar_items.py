# generar_items.py - Script para generar tokens y códigos
import os
import django
import csv

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'identylog_project.settings')
django.setup()

from nfc_manager.models import NFCBatch, NFCItem
from nfc_manager.utils.nfc_generator import generate_secure_token, generate_activation_code, hash_activation_code

def generar_items_para_lote(batch_id, cantidad=None):
    """Genera items para un lote existente"""
    
    # Buscar el lote
    try:
        batch = NFCBatch.objects.get(id=batch_id)
    except NFCBatch.DoesNotExist:
        print(f"❌ Error: No existe el lote con ID {batch_id}")
        return
    
    print(f"\n🚀 Generando items para lote: {batch.name}")
    print(f"📦 Tipo: {batch.support_type}")
    print(f"🔢 Cantidad a generar: {cantidad or batch.quantity}\n")
    
    # Si no se especifica cantidad, usar la del lote
    if cantidad is None:
        cantidad = batch.quantity
    
    items_to_create = []
    codes_for_csv = []
    
    for i in range(cantidad):
        # Generar token único
        token = generate_secure_token()
        
        # Generar código de activación
        plain_code = generate_activation_code()
        
        # Guardar código de forma segura
        hashed_code = hash_activation_code(plain_code)
        
        # Crear item
        item = NFCItem(
            batch=batch,
            public_token=token,
            activation_code_hash=hashed_code,
            status='inactive'
        )
        items_to_create.append(item)
        
        # Guardar para CSV
        codes_for_csv.append({
            'token': token,
            'url': f'http://127.0.0.1:8000/t/{token}',
            'codigo': plain_code,
            'tipo': batch.support_type
        })
        
        if (i + 1) % 10 == 0:
            print(f"   Generados {i + 1} de {cantidad}...")
    
    # Guardar todos los items de una vez
    NFCItem.objects.bulk_create(items_to_create)
    
    print(f"\n✅ {len(items_to_create)} items creados correctamente")
    
    # Generar CSV
    csv_filename = f'lote_{batch.id}_{batch.name.replace(" ", "_")}.csv'
    csv_path = os.path.join(os.path.expanduser('~'), 'Desktop', csv_filename)
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['TOKEN (va en NFC)', 'URL COMPLETA', 'CÓDIGO ACTIVACIÓN (imprimir)', 'TIPO'])
        
        for item_data in codes_for_csv:
            writer.writerow([
                item_data['token'],
                item_data['url'],
                item_data['codigo'],
                item_data['tipo']
            ])
    
    print(f"📄 CSV guardado en: {csv_path}")
    
    # Mostrar ejemplos
    print("\n🔍 PRIMEROS 3 ITEMS:")
    for i, item_data in enumerate(codes_for_csv[:3]):
        print(f"\n   {i+1}. Token: {item_data['token']}")
        print(f"      URL: {item_data['url']}")
        print(f"      Código: {item_data['codigo']}")
    
    print(f"\n✨ ¡Listo! Tienes {len(items_to_create)} soportes listos para enviar al proveedor NFC.\n")
    
    return codes_for_csv

if __name__ == '__main__':
    print("=" * 50)
    print("   GENERADOR DE ITEMS NFC")
    print("=" * 50)
    
    # Pedir el ID del lote
    batch_id = input("\n📝 ID del lote (mira en /admin/nfc_manager/nfcbatch/): ")
    
    try:
        batch_id = int(batch_id)
    except:
        print("❌ El ID debe ser un número")
        exit()
    
    # Pedir cantidad (opcional)
    cantidad_input = input("Cantidad a generar (Enter para usar la del lote): ")
    cantidad = int(cantidad_input) if cantidad_input else None
    
    # Generar
    generar_items_para_lote(batch_id, cantidad)
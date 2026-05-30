# nfc_generator.py - El corazón que crea los códigos
import secrets
import bcrypt
from django.db import IntegrityError

def generate_activation_code():
    """
    Genera un código como: AMOR-8372
    Fácil de leer, imposible de adivinar
    """
    # Lista de palabras bonitas para los códigos
    palabras = ['AMOR', 'LUNA', 'SOL', 'FLOR', 'PULSO', 'VIDA', 'RISA', 'PIEZ', 
                'ALMA', 'RÍO', 'CIEL', 'MAR', 'NUBE', 'LUZ', 'SON', 'PAZ']
    
    import random
    palabra = random.choice(palabras)
    numero = random.randint(1000, 9999)
    return f"{palabra}-{numero}"

def generate_secure_token():
    """
    Genera un token público como: aB3xY9kLmN
    Esto es lo que va grabado en el NFC
    """
    # 12 caracteres aleatorios seguros
    token = secrets.token_urlsafe(9)[:12]
    return token

def hash_activation_code(code):
    """
    Convierte el código en algo ilegible pero válido
    Nadie puede ver el código original después de esto
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(code.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_activation_code(plain_code, hashed_code):
    """
    Verifica si un código escrito por el usuario es correcto
    Devuelve True o False
    """
    try:
        return bcrypt.checkpw(plain_code.encode('utf-8'), hashed_code.encode('utf-8'))
    except:
        return False
# models.py - COMPLETO Y FUNCIONAL
from django.db import models
from django.contrib.auth.models import User

class NFCBatch(models.Model):
    """Un lote = muchas pulseras/pegatinas juntas"""
    name = models.CharField(max_length=200)
    support_type = models.CharField(max_length=50)  # pulsera, pegatina, tarjeta, llavero
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.support_type}) - {self.quantity} unidades"


class NFCItem(models.Model):
    """Cada pulsera/pegatina individual"""
    
    STATUS_CHOICES = [
        ('inactive', 'Sin activar'),
        ('active', 'Activado'),
        ('blocked', 'Bloqueado'),
    ]
    
    # El token público que va grabado en el NFC (ej: aB3xY9kLmN)
    public_token = models.CharField(max_length=20, unique=True)
    
    # El código que el usuario tiene que escribir (guardado SEGURO)
    activation_code_hash = models.CharField(max_length=255)
    
    # A qué lote pertenece
    batch = models.ForeignKey(NFCBatch, on_delete=models.CASCADE, related_name='items')
    
    # Estado actual
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    
    # Usuario que lo activó (puede ser null si nadie lo ha activado)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.public_token} - {self.get_status_display()}"
    
    @property
    def public_url(self):
        """Devuelve la URL completa que va en el NFC"""
        return f"https://identylog.com/t/{self.public_token}"


class Moment(models.Model):
    """El vídeo + mensaje asociado a un NFC"""
    
    nfc_item = models.OneToOneField(NFCItem, on_delete=models.CASCADE, related_name='moment')
    title = models.CharField(max_length=200, blank=True, null=True)
    recipient_name = models.CharField(max_length=100, blank=True, null=True)  # Para quién es
    sender_name = models.CharField(max_length=100, blank=True, null=True)     # Quién lo envía
    message = models.TextField(blank=True, null=True)
    # Dentro de la clase Moment, añade esta línea:
    views_count = models.IntegerField(default=0)  # Número de veces que se vio el vídeo
    # Video de YouTube
    youtube_url = models.URLField(blank=True, null=True)
    youtube_embed_url = models.URLField(blank=True, null=True)
    youtube_video_id = models.CharField(max_length=50, blank=True, null=True)
    
    # Estado del contenido
    is_active = models.BooleanField(default=True)  # Si el usuario lo desactiva temporalmente
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title or f"Moment for {self.nfc_item.public_token}"
    
    def extract_youtube_id(self, url):
        """Extrae el ID del vídeo de YouTube desde cualquier formato de URL"""
        if not url:
            return None
        
        # Casos: youtube.com/watch?v=XXX, youtu.be/XXX, etc
        if 'youtu.be' in url:
            return url.split('/')[-1].split('?')[0]
        elif 'watch?v=' in url:
            return url.split('watch?v=')[1].split('&')[0]
        elif 'embed/' in url:
            return url.split('embed/')[1].split('?')[0]
        return None
    
    def save(self, *args, **kwargs):
        """Antes de guardar, procesa la URL de YouTube"""
        if self.youtube_url:
            video_id = self.extract_youtube_id(self.youtube_url)
            if video_id:
                self.youtube_video_id = video_id
                self.youtube_embed_url = f"https://www.youtube.com/embed/{video_id}"
        super().save(*args, **kwargs)
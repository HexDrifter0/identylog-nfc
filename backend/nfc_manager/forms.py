# forms.py - Formularios personalizados
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    """Formulario de registro con estilos y mejores mensajes"""
    
    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: maria_lopez',
            'autocomplete': 'off'
        })
    )
    
    email = forms.EmailField(
        label='Correo electrónico',
        required=False,
        widget=forms.EmailInput(attrs={
            'placeholder': 'tu@email.com'
        })
    )
    
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mínimo 8 caracteres'
        })
    )
    
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Escribe la contraseña otra vez'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clases CSS a todos los campos
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
    
    def clean_username(self):
        """Verificar que el usuario no exista"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('❌ Este nombre de usuario ya está en uso. Elige otro.')
        return username
    
    def clean_password1(self):
        """Verificar que la contraseña sea segura"""
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise forms.ValidationError('❌ La contraseña debe tener al menos 8 caracteres.')
        return password
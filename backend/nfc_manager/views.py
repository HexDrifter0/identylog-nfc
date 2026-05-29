# views.py - Toda la lógica de negocio
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import NFCItem, Moment
from .forms import CustomUserCreationForm
from .utils.nfc_generator import check_activation_code

LANDING_TEMPLATE = 'nfc_manager/landing.html'
ACTIVATE_TEMPLATE = 'nfc_manager/activate.html'


def landing_inicio(request):
    """Página de bienvenida pública."""
    return render(request, 'nfc_manager/landing_inicio.html')


def landing_publica(request, token):
    """Vista pública que ve quien escanea el NFC."""
    nfc_item = get_object_or_404(NFCItem, public_token=token)

    if nfc_item.status == 'blocked':
        return render(request, LANDING_TEMPLATE, {
            'error': 'Este soporte ha sido bloqueado. Contacta con Identylog.'
        })

    if nfc_item.status == 'inactive':
        return redirect('activar_soporte', token=token)

    try:
        momento = Moment.objects.get(nfc_item=nfc_item)
        is_owner = request.user == nfc_item.user if request.user.is_authenticated else False
        cookie_name = f'viewed_{token}'

        if not request.COOKIES.get(cookie_name) and not is_owner:
            momento.views_count += 1
            momento.save()

        response = render(request, LANDING_TEMPLATE, {'momento': momento})

        if not request.COOKIES.get(cookie_name):
            response.set_cookie(cookie_name, '1', max_age=86400, httponly=True)

        return response
    except Moment.DoesNotExist:
        return render(request, LANDING_TEMPLATE, {'momento': None})


def activar_soporte(request, token):
    """Pantalla donde el usuario introduce el código de activación."""
    nfc_item = get_object_or_404(NFCItem, public_token=token)

    if nfc_item.status != 'inactive':
        return redirect('landing_publica', token=token)

    if request.method == 'POST':
        codigo = request.POST.get('activation_code', '').strip().upper()

        if check_activation_code(codigo, nfc_item.activation_code_hash):
            nfc_item.status = 'active'
            if request.user.is_authenticated:
                nfc_item.user = request.user
            nfc_item.save()
            Moment.objects.create(nfc_item=nfc_item)
            messages.success(request, '✅ ¡Soporte activado! Ahora puedes añadir tu vídeo.')
            return redirect('dashboard') if request.user.is_authenticated else redirect('registro')
        messages.error(request, '❌ Código incorrecto. Revisa la tarjeta e inténtalo de nuevo.')

    return render(request, ACTIVATE_TEMPLATE, {'token': token})


def registro(request):
    """Registro de nuevos usuarios con mensajes claros."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '🎉 ¡Bienvenido a Identylog! Tu cuenta ha sido creada.')
            next_url = request.GET.get('next')
            return redirect(next_url or 'dashboard')
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{error}')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """Inicio de sesión."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'👋 ¡Bienvenido de nuevo, {user.username}!')
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    """Cerrar sesión."""
    logout(request)
    messages.success(request, '👋 ¡Hasta luego!')
    return redirect('landing_inicio')


@login_required
def dashboard(request):
    """Panel de control del usuario."""
    momentos = Moment.objects.filter(nfc_item__user=request.user)
    return render(request, 'nfc_manager/dashboard.html', {'momentos': momentos})


@login_required
def editar_momento(request, momento_id):
    """Editar vídeo y mensaje de un recuerdo."""
    momento = get_object_or_404(Moment, id=momento_id, nfc_item__user=request.user)

    if request.method == 'POST':
        momento.title = request.POST.get('title', '')
        momento.youtube_url = request.POST.get('youtube_url', '')
        momento.message = request.POST.get('message', '')
        momento.recipient_name = request.POST.get('recipient_name', '')
        momento.save()
        messages.success(request, '✨ ¡Tu recuerdo se ha actualizado!')
        return redirect('dashboard')

    return render(request, 'nfc_manager/editar_momento.html', {'momento': momento})

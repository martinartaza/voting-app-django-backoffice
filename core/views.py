from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Company
from allauth.socialaccount.models import SocialAccount


def index(request):
    """
    Vista principal de la aplicación
    """
    return render(request, 'index.html')


def custom_github_login(request):
    """
    Redirige a la URL de login de GitHub con el parámetro 'state'.
    """
    state_param = request.GET.get('state', '')
    print(f"🔗 CustomGitHubLogin - State recibido: {state_param}")
    
    # Guardar el state personalizado en la sesión ANTES de enviarlo a allauth
    if state_param:
        request.session['custom_oauth_state'] = state_param
        print(f"💾 CustomGitHubLogin - State guardado en sesión: {state_param}")
    
    # Construye la URL de login de allauth
    url = reverse('github_login')
    url += '?process=login'
    
    if state_param:
        url += f'&state={state_param}'
        print(f"🔗 CustomGitHubLogin - URL final con state: {url}")
    else:
        print(f"🔗 CustomGitHubLogin - URL final sin state: {url}")
        
    return redirect(url)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_company_uuid(request):
    """
    Obtiene el UUID de la empresa del usuario autenticado
    """
    user = request.user
    
    if not user.company:
        return JsonResponse({'error': 'Usuario no pertenece a ninguna empresa'}, status=404)
    
    return JsonResponse({
        'company_uuid': user.company.id,
        'company_name': user.company.name
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])  # Restaurar autenticación
def create_tokens(request):
    """
    Crea tokens JWT para el usuario autenticado
    """
    print("/n/n/n Paso por aqui /n/n/n", flush=True)
    
    user = request.user
    refresh = RefreshToken.for_user(user)
    json = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'company': user.company.name if user.company else None,
        }
    }
    print(json)
    return JsonResponse({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'company': user.company.name if user.company else None,
        }
    })


@login_required
def profile(request):
    """
    Vista del perfil del usuario
    """
    return render(request, 'profile.html', {'user': request.user})
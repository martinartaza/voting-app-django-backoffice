from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
from .models import Company


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adaptador personalizado para manejar usuarios de social login
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Se ejecuta ANTES del login social
        - Recupera el state de la sesión
        - Crea la empresa si es necesario
        - Guarda la empresa en la sesión
        """
        print(f"🔔 Adapter - pre_social_login - Provider: {sociallogin.account.provider}")
        
        if sociallogin.account.provider == 'github':
            # Obtener el state personalizado de la sesión
            state_param = request.session.get('custom_oauth_state', '')
            print(f"🔔 Adapter - State de sesión: {state_param}")
            
            if state_param and 'company_name=' in state_param:
                # Procesar el state para crear empresa
                company_name = state_param.split('company_name=')[1]
                company_name = company_name.replace('%20', ' ')  # Decodificar espacios
                print(f"🏢 Adapter - Creando empresa: {company_name}")
                
                # Crear la empresa (o obtenerla si ya existe)
                company, created = Company.objects.get_or_create(name=company_name)
                if created:
                    print(f"✅ Adapter - Empresa creada con ID: {company.id}")
                else:
                    print(f"✅ Adapter - Empresa existente encontrada: {company.name}")
                
                # Guardar la empresa en la sesión para usarla en save_user
                request.session['pending_company_id'] = company.id
                request.session['pending_user_role'] = 'COMPANY_ADMIN'
                print(f"💾 Adapter - Empresa guardada en sesión: {company.id}")
            
            elif state_param and 'company_uuid=' in state_param:
                # Procesar el state para unirse a empresa existente
                company_uuid = state_param.split('company_uuid=')[1]
                print(f"👥 Adapter - Uniendo a empresa UUID: {company_uuid}")
                
                try:
                    # Buscar la empresa por UUID
                    company = Company.objects.get(id=company_uuid)
                    print(f"✅ Adapter - Empresa encontrada: {company.name}")
                    
                    # Guardar la empresa en la sesión para usarla en save_user
                    request.session['pending_company_id'] = company.id
                    request.session['pending_user_role'] = 'COMMON_USER'
                    print(f"💾 Adapter - Empresa guardada en sesión: {company.id}")
                    
                except Company.DoesNotExist:
                    print(f"❌ Adapter - Empresa con UUID {company_uuid} no encontrada")
                except Exception as e:
                    print(f"❌ Adapter - Error procesando empresa: {e}")
    
    def save_user(self, request, sociallogin, form=None):
        """
        Se ejecuta DESPUÉS de crear el usuario
        - Recupera la empresa de la sesión
        - Asigna el usuario a la empresa
        - Establece el rol
        - Limpia la sesión
        """
        print(f"💾 Adapter - save_user - Usuario: {sociallogin.user.username}")
        
        # Llamar al método padre para crear el usuario
        user = super().save_user(request, sociallogin, form)
        
        # Recuperar la empresa de la sesión
        company_id = request.session.get('pending_company_id')
        user_role = request.session.get('pending_user_role')
        
        if company_id and user_role:
            try:
                # Buscar la empresa
                company = Company.objects.get(id=company_id)
                print(f"🏢 Adapter - Asignando usuario a empresa: {company.name}")
                
                # Asignar usuario a la empresa
                user.company = company
                user.role = user_role
                user.save()
                
                print(f"✅ Adapter - Usuario '{user.username}' asignado como {user_role} a empresa '{company.name}'")
                
                # Limpiar la sesión
                if 'pending_company_id' in request.session:
                    del request.session['pending_company_id']
                if 'pending_user_role' in request.session:
                    del request.session['pending_user_role']
                if 'custom_oauth_state' in request.session:
                    del request.session['custom_oauth_state']
                print(f"🧹 Adapter - Sesión limpiada")
                
            except Company.DoesNotExist:
                print(f"❌ Adapter - Empresa con ID {company_id} no encontrada")
            except Exception as e:
                print(f"❌ Adapter - Error asignando usuario a empresa: {e}")
        
        return user


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Adaptador personalizado para manejar la redirección después del login
    """
    
    def get_login_redirect_url(self, request):
        """
        Redirige al home después del login exitoso
        """
        return '/'

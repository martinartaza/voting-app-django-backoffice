from django.utils.deprecation import MiddlewareMixin
from urllib.parse import parse_qs, urlparse

class OAuthStateMiddleware(MiddlewareMixin):
    """
    Middleware para procesar el parámetro state del OAuth de GitHub
    """
    
    def process_request(self, request):
        # No necesitamos procesar nada en el request
        return None
    
    def process_response(self, request, response):
        # Solo procesar después de un login exitoso
        if (hasattr(request, 'user') and 
            request.user.is_authenticated and 
            '/accounts/github/login/callback/' in request.path):
            
            print(f"✅ OAuthStateMiddleware - process_response - Usuario autenticado: {request.user.username}")
            
            # Obtener nuestro state personalizado de la sesión
            custom_state = request.session.get('custom_oauth_state', '')
            print(f"🔍 OAuthStateMiddleware - process_response - Custom state de sesión: {custom_state}")
            
            if custom_state:
                # Procesar nuestro state personalizado
                self.process_oauth_state(request, custom_state)
                # Limpiar el state de la sesión
                if 'custom_oauth_state' in request.session:
                    del request.session['custom_oauth_state']
                    print(f"🧹 OAuthStateMiddleware - Custom state limpiado de sesión")
            else:
                print(f"⚠️ OAuthStateMiddleware - No hay custom state en sesión")
        
        return response
    
    def process_oauth_state(self, request, state):
        """Procesa el parámetro state según el escenario"""
        print(f"🔄 OAuthStateMiddleware - Procesando state: {state}")
        
        if not state:
            print(f"❌ OAuthStateMiddleware - State vacío")
            return
        
        try:
            # Parsear el state
            if 'company_name=' in state:
                # Escenario 1: Crear nueva empresa
                company_name = state.split('company_name=')[1]
                company_name = company_name.replace('%20', ' ')  # Decodificar espacios
                print(f"🏢 OAuthStateMiddleware - Creando empresa: {company_name}")
                self.create_company_and_assign_user(request.user, company_name)
                
            elif 'company_uuid=' in state:
                # Escenario 2: Unirse a empresa existente
                company_uuid = state.split('company_uuid=')[1]
                print(f"👥 OAuthStateMiddleware - Uniendo a empresa UUID: {company_uuid}")
                self.assign_user_to_existing_company(request.user, company_uuid)
            else:
                print(f"❓ OAuthStateMiddleware - State no reconocido: {state}")
                
        except Exception as e:
            print(f"❌ OAuthStateMiddleware - Error procesando state: {e}")
    
    def create_company_and_assign_user(self, user, company_name):
        """Crea una nueva empresa y asigna al usuario como COMPANY_ADMIN"""
        from .models import Company
        
        print(f"🏗️ OAuthStateMiddleware - Creando empresa: {company_name}")
        
        # Crear la empresa
        company = Company.objects.create(name=company_name)
        print(f"✅ OAuthStateMiddleware - Empresa creada con ID: {company.id}")
        
        # Asignar usuario a la empresa como COMPANY_ADMIN
        user.company = company
        user.role = 'COMPANY_ADMIN'
        user.save()
        
        print(f"✅ OAuthStateMiddleware - Usuario '{user.username}' asignado como COMPANY_ADMIN a empresa '{company_name}'")
    
    def assign_user_to_existing_company(self, user, company_uuid):
        """Asigna el usuario a una empresa existente como COMMON_USER"""
        from .models import Company
        
        print(f"🔍 OAuthStateMiddleware - Buscando empresa con UUID: {company_uuid}")
        
        try:
            # Buscar la empresa por UUID
            company = Company.objects.get(id=company_uuid)
            print(f"✅ OAuthStateMiddleware - Empresa encontrada: {company.name}")
            
            # Asignar usuario a la empresa como COMMON_USER
            user.company = company
            user.role = 'COMMON_USER'
            user.save()
            
            print(f"✅ OAuthStateMiddleware - Usuario '{user.username}' asignado como COMMON_USER a empresa '{company.name}'")
            
        except Company.DoesNotExist:
            print(f"❌ OAuthStateMiddleware - Empresa con UUID {company_uuid} no encontrada")
        except Exception as e:
            print(f"❌ OAuthStateMiddleware - Error asignando usuario a empresa: {e}")

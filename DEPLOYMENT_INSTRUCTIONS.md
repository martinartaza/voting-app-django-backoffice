# 🚀 Instrucciones de Despliegue a Google Cloud Run

## 📋 Resumen de Cambios Realizados

Este proyecto ha sido actualizado y corregido para ser desplegado en Google Cloud Run desde Bitbucket privado. Los siguientes archivos fueron modificados:

### ✅ Archivos Actualizados:

1. **`requirements.txt`** - Actualizado con todas las dependencias del virtualenv `whatsapp`
2. **`docker-compose.yml`** - Corregido para usar Python y comandos correctos
3. **`entrypoint.sh`** - Configurado para usar Gunicorn en puerto 8080 + opción de reset de DB
4. **`config/settings.py`** - DEBUG desde env var + ALLOWED_HOSTS con Cloud Run domains
5. **`env.example`** - Actualizado con todas las variables necesarias incluyendo RESET_DATABASE
6. **`cloudbuild.yaml`** - Preparado para Bitbucket (requiere actualizar URL después de push)

---

## 📝 Paso 1: Subir a Bitbucket

### 1.1 Crear el repositorio en Bitbucket (si no existe)
```bash
# Ir a https://bitbucket.org y crear un nuevo repositorio privado
# Nombre sugerido: voting-django-backoffice
```

### 1.2 Agregar remote y push
```bash
# Agregar remote de Bitbucket
git remote add bitbucket https://bitbucket.org/YOUR_WORKSPACE/voting-django-backoffice.git

# Verificar branch actual
git branch

# Push a Bitbucket
git push bitbucket social_login_github:main
# O si prefieres crear un branch nuevo:
# git push bitbucket HEAD:main
```

---

## 🔧 Paso 2: Configurar Terraform (Proyecto separado)

Después de subir a Bitbucket, ve a tu proyecto de Terraform (`voting-terraform-django`) y actualiza:

### 2.1 Actualizar `cloudbuild.yaml` en Terraform

En el archivo `cloudbuild.yaml`, cambiar la línea 22:
```yaml
# ANTES:
- 'https://github.com/martinartaza/voting-app-django-backoffice.git'

# DESPUÉS:
- 'https://bitbucket.org/YOUR_WORKSPACE/voting-django-backoffice.git'
```

### 2.2 Configurar credenciales de Bitbucket en Google Cloud

#### Opción A: Usar Secret Manager (Recomendado para repo privado)

```bash
# Crear secrets para Bitbucket
gcloud secrets create bitbucket-username --data-file=- <<< "tu_usuario_bitbucket"
gcloud secrets create bitbucket-app-password --data-file=- <<< "tu_app_password"

# Dar permisos a Cloud Build
gcloud secrets add-iam-policy-binding bitbucket-username \
  --member="serviceAccount:YOUR_PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding bitbucket-app-password \
  --member="serviceAccount:YOUR_PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

Luego descomentar las líneas en `cloudbuild.yaml`:
```yaml
availableSecrets:
  secretManager:
  - versionName: projects/$PROJECT_ID/secrets/bitbucket-username/versions/latest
    env: 'BITBUCKET_USERNAME'
  - versionName: projects/$PROJECT_ID/secrets/bitbucket-app-password/versions/latest
    env: 'BITBUCKET_APP_PASSWORD'
```

#### Opción B: Conectar repositorio de Bitbucket directamente
Seguir guía oficial: https://cloud.google.com/build/docs/automating-builds/bitbucket/connect-repo-bitbucket

---

## 🗄️ Paso 3: Primer Despliegue (Borrar DB del proyecto anterior)

### 3.1 En Terraform, agregar la variable de entorno `RESET_DATABASE=true`

En tu configuración de Terraform para el servicio de Cloud Run, agregar:

```hcl
resource "google_cloud_run_service" "django_service" {
  # ... otras configuraciones ...
  
  template {
    spec {
      containers {
        # ... otras configuraciones ...
        
        env {
          name  = "RESET_DATABASE"
          value = "true"  # ← SOLO PARA EL PRIMER DEPLOY
        }
        
        # ... resto de variables de entorno ...
      }
    }
  }
}
```

### 3.2 Aplicar Terraform

```bash
cd /path/to/voting-terraform-django
terraform plan
terraform apply
```

### 3.3 Verificar logs en Cloud Run

```bash
# Ver logs del despliegue
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=django-service" --limit 50 --format json
```

Buscar el mensaje: `⚠️  RESET_DATABASE is enabled - Dropping all tables...`

---

## 🔒 Paso 4: IMPORTANTE - Remover RESET_DATABASE después del primer deploy

### 4.1 Actualizar Terraform

En tu configuración de Terraform, **REMOVER** o **COMENTAR** la variable `RESET_DATABASE`:

```hcl
resource "google_cloud_run_service" "django_service" {
  # ... otras configuraciones ...
  
  template {
    spec {
      containers {
        # ... otras configuraciones ...
        
        # env {
        #   name  = "RESET_DATABASE"
        #   value = "true"  # ← COMENTADO DESPUÉS DEL PRIMER DEPLOY
        # }
        
        # ... resto de variables de entorno ...
      }
    }
  }
}
```

### 4.2 Aplicar cambios

```bash
terraform plan
terraform apply
```

---

## 🌐 Variables de Entorno Requeridas en Cloud Run

Asegúrate de que tu Terraform configure estas variables de entorno en Cloud Run:

### Obligatorias:
- `DJANGO_DEBUG=False`
- `DJANGO_SECRET_KEY=<tu-secret-key-produccion>`
- `DB_NAME=<nombre-db>`
- `DB_USER=<usuario-db>`
- `DB_PASSWORD=<password-db>`
- `DB_HOST=<cloud-sql-connection-name>`
- `DB_PORT=5432`
- `CUSTOM_DOMAIN=django.sebastianartaza.com`
- `PRODUCTION_DOMAIN=django.sebastianartaza.com`

### Para Django Superuser:
- `DJANGO_SUPERUSER_USERNAME=admin`
- `DJANGO_SUPERUSER_EMAIL=admin@example.com`
- `DJANGO_SUPERUSER_PASSWORD=<password-seguro>`
- `DJANGO_SUPERUSER_COMPANY=Default Company`

### Para Email (Resend):
- `RESEND_API_KEY=<tu-api-key>`
- `RESEND_FROM_EMAIL=noreply@yourdomain.com`
- `RESEND_FROM_NAME=Voting System`

### Para GitHub OAuth:
- `CLIENT_ID_GITHUB=<tu-client-id>`
- `CLIENT_SECRET_GITHUB=<tu-client-secret>`

### Solo para el primer deploy:
- `RESET_DATABASE=true` (remover después del primer deploy exitoso)

---

## 🧪 Verificación del Despliegue

### 1. Verificar que el servicio esté corriendo
```bash
gcloud run services describe django-service --region=us-central1
```

### 2. Acceder a la aplicación
```bash
# Obtener la URL del servicio
gcloud run services describe django-service --region=us-central1 --format='value(status.url)'
```

### 3. Probar endpoints
```bash
# Health check
curl https://django-service-xxxxx-uc.a.run.app/

# Admin panel
curl https://django-service-xxxxx-uc.a.run.app/admin/
```

---

## 📚 Recursos Adicionales

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Connecting to Cloud SQL from Cloud Run](https://cloud.google.com/sql/docs/postgres/connect-run)
- [Bitbucket Cloud Build Integration](https://cloud.google.com/build/docs/automating-builds/bitbucket/connect-repo-bitbucket)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)

---

## ❓ Troubleshooting

### Error: "Could not connect to database"
- Verificar que Cloud SQL esté corriendo
- Verificar que las credenciales de DB sean correctas
- Verificar que Cloud Run tenga acceso a Cloud SQL (VPC connector o Cloud SQL Proxy)

### Error: "DisallowedHost"
- Verificar que `CUSTOM_DOMAIN` esté configurado
- Verificar que `.run.app` domains estén en ALLOWED_HOSTS

### Error: "CSRF verification failed"
- Verificar `CSRF_TRUSTED_ORIGINS` en settings.py
- Verificar que `CLOUD_RUN_SERVICE_URL` esté configurado

### El RESET_DATABASE no borró las tablas
- Verificar logs de Cloud Run
- Verificar que la variable de entorno esté en "true" (lowercase)
- Verificar permisos de DB user para DROP tables

---

## ✅ Checklist Final

- [ ] Código subido a Bitbucket
- [ ] `cloudbuild.yaml` actualizado con URL de Bitbucket
- [ ] Credenciales de Bitbucket configuradas en Google Cloud
- [ ] Variables de entorno configuradas en Terraform
- [ ] `RESET_DATABASE=true` configurado para primer deploy
- [ ] Terraform apply ejecutado exitosamente
- [ ] Logs verificados - DB reset exitoso
- [ ] `RESET_DATABASE` removido de variables de entorno
- [ ] Segundo Terraform apply ejecutado
- [ ] Aplicación funcionando correctamente
- [ ] Admin panel accesible
- [ ] OAuth GitHub funcionando

---

## 📧 Contacto

Si encuentras algún problema durante el despliegue, revisa los logs de Cloud Run:

```bash
gcloud logging read "resource.type=cloud_run_revision" --limit 100 --format json
```

¡Éxito con tu despliegue! 🎉


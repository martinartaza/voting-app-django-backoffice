# **Sistema de Votación MVP - Backoffice Django**

Este repositorio contiene la implementación del backoffice para un
Sistema de Votación, desarrollado con Django. Es el primer componente de
un ambicioso proyecto MVP (Producto Mínimo Viable) diseñado para
demostrar habilidades en diversas tecnologías modernas.

## **Descripción del Proyecto**

El objetivo de este sistema es permitir que los departamentos de
Recursos Humanos de una empresa puedan crear y gestionar competiciones
de votación (ej. \"Mejor Compañero del Año\"), donde los empleados
puedan votar por sus colegas.

Este backoffice de Django proporciona la interfaz de administración
para:

- Gestionar **Competiciones** (fechas, nombres).

- Gestionar **Votos** (títulos, descripciones, premios).

- Administrar **Empresas** y sus usuarios.

- Gestionar **Usuarios** con distintos roles:

  - **Administrador Global**: Control total del sistema (solo el
    > desarrollador).

  - **Administrador de Empresa**: Puede gestionar usuarios y
    > competiciones dentro de su empresa.

  - **Usuario Común**: Participa en las votaciones (a través de la
    > futura aplicación móvil).

## **Tecnologías Utilizadas**

- **Python 3.9+**

- **Django 4.2.x**: Framework web para el backoffice.

- **PostgreSQL**: Base de datos relacional.

- **Gunicorn**: Servidor WSGI para producción.

- **WhiteNoise**: Para servir archivos estáticos en producción.

- **pytest**: Framework de testing para Python.

- **pytest-django**: Plugin para integrar pytest con Django.

- **python-dotenv**: Para la gestión de variables de entorno.

## **Estructura del Proyecto**

El proyecto sigue una estructura estándar de Django:

> .  
├── config/ \# Configuración principal del proyecto Django  
├── core/ \# Aplicación principal del sistema de votación (modelos,
vistas, admin)  
├── templates/ \# Plantillas HTML globales (base.html, index.html,
404.html)  
├── src/ \# Archivos estáticos a nivel de proyecto (ej. CSS global)  
│ └── css/  
│ │   └── styles.css  
├── .env.example \# Plantilla de variables de entorno  
├── Dockerfile \# Definición de la imagen Docker de la aplicación  
├── docker-compose.yml \# Configuración para levantar la aplicación y la
DB en Docker local  
├── manage.py \# Utilidad de línea de comandos de Django  
├── pytest.ini \# Configuración de pytest  
└── .coveragerc \# Configuración de cobertura de código

## **Cómo Ejecutar Localmente con Docker Compose**

Para levantar el proyecto en tu máquina local usando Docker:

1.  **Clona el repositorio:**  
    > git clone
    > https://github.com/martinartaza/voting-app-django-backoffice.git  
    > cd voting-app-django-backoffice

2.  Crea el archivo .env:  
    > Copia el contenido de .env.example a un nuevo archivo llamado .env
    > en la raíz del proyecto y rellena los valores.  
    > cp .env.example .env  
    > \# Edita .env con tus valores

3.  Levanta los servicios Docker:  
    > Esto construirá la imagen de Docker, instalará las dependencias,
    > ejecutará las migraciones de Django, recolectará los archivos
    > estáticos y levantará el servidor Gunicorn junto con una base de
    > datos PostgreSQL.  
    > docker-compose up \--build

4.  Accede a la aplicación:  
    > Una vez que los servicios estén levantados, podrás acceder al
    > backoffice de Django en tu navegador:

    - Página de inicio: http://localhost:8000/

    - Panel de administración: http://localhost:8000/admin/

5.  Crear un superusuario (si es la primera vez o la DB está vacía):  
    > Abre otra terminal en el mismo directorio del proyecto y
    > ejecuta:  
    > docker-compose exec web python manage.py createsuperuser

## **Tests**

Este proyecto incluye tests unitarios y de integración para asegurar la
calidad del código.

Para ejecutar los tests:

docker-compose exec web pytest -v

## **Próximos Pasos (Hoja de Ruta del MVP)**

Este backoffice es el primer pilar de un sistema más grande. Los
siguientes pasos incluyen:

- **Despliegue en AWS App Runner con AWS RDS (gestionado por
  > Terraform):** El objetivo es automatizar la infraestructura y el
  > despliegue en la nube.

- **API REST con FastAPI y AWS Lambda:** Desarrollo de los endpoints
  > necesarios para la aplicación móvil.

- **Aplicación Móvil con Flutter:** La interfaz de usuario para que los
  > empleados puedan votar.

- **CI/CD con Terraform:** Automatización de los pipelines de
  > integración y despliegue continuo.

## **Contacto**

Sebastian Martin, Artaza Saade

Linkedin: https://www.linkedin.com/in/sebastian-martin-artaza-saade-7b482123/

Github: https://github.com/martinartaza

Sitio Web Personal: https://www.sebastianartaza.com https://n8n.sebastianartaza.com





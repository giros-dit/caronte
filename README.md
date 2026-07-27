# Caronte

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./static/caronte-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="./static/caronte-light.png">
  <img alt="Shows a black logo in light color mode and a white one in dark color mode." src="./static/caronte.png">
</picture>

Caronte es un aplicación que posibilita el encendido remoto de ordenadores, monitorizar el estado de los mismos y la gestión de usuarios y sus permisos, todo ello desde un interfaz web. 

## Instalación
La aplicación solo admite su despliegue mediante la imagen de docker:

```bash
docker run -p 3000:3000 -v ./data:/app/data ghcr.io/giros-dit/caronte:latest
```

## Configuración
Caronte admite las siguientes variables de entorno:

 Variable | Descripción | Valor por defecto 
----------|-------------|-------------------
 SERVER_NAME | String con el nombre del servidor | `Wake on LAN Server` 
 SERVER_URL | URL de acceso al servidor, incluyendo el puerto | `http://localhost:3000`
 MAIL_FROM | Dirección de envío de mensajes. Admite formato `Example <noreply@example.com>` | `-`
 MAIL_SERVER | Servidor SMTP para envío de emails | `-`
 MAIL_PORT | Puerto de conexión del servidor SMTP | `25`
 MAIL_USE_TLS | Uso de TLS en la conexión con el servidor SMTP | `False`
 MAIL_USER | Usuario del servidor SMTP | `-`
 MAIL_PASS | Contraseña del servidor SMTP | `-`
 SECRET | Secreto de la sesión de Flask. Si cambia, los usuarios deberán volver a a autenticarse. | Se generará automáticamente en cada arranque mediante `os.urandom(32)`.
 SESSION_COOKIE_SECURE | Admitir solo conexiones HTTPS para el intercambio de cookies. | `False`
 SESSION_COOKIE_HTTPONLY | Evita que los scripts accedan a las cookies de sesión. | `True`
 SESSION_COOKIE_SAMESITE | Controla el intercambio de cookies en peticiones *cross-site*. | `Lax`
 OIDC_ENABLED | Habilita la autenticación mediante OIDC. | `False`
 OIDC_SCOPES | Scopes por defecto de OIDC. | `openid email profile`
 OIDC_CLIENT_SECRETS | Fichero de secretos del cliente OIDC. Más información [aquí](#autenticación-mediante-oidc). | `./data/client_secrets.json`
 OIDC_PATH_PREFIX | Prefijo de ruta para la autenticación OIDC. Si se deja vacío, no podrá usarse la autenticación local. | `/oidc`
 OIDC_OVERWRITE_REDIRECT_URI | URL de redirección de OIDC. Esta debe configurarse en el servicio OIDC. | `http://localhost:3000/oidc/authorize`
 OIDC_ADMIN_GROUPS | Grupos de OIDC (separados por espacios) cuyos usuarios obtendrán permisos de administrador en el próximo inicio de sesión. | `-`
 OIDC_SERVICE_GROUPS | Grupos de OIDC (separados por espacios) cuyos usuarios serán tratados como cuentas de servicio. | `-`
 OIDC_RECOVER_PASSWORD_URL | URL de recuperación de contraseña de OIDC para la página de recuperación. | `-`
 LOG_LEVEL | Controla el nivel de severidad de las trazas. | `INFO`

 ## Autenticación mediante OIDC
Para usar autenticación mediante OIDC, la aplicación espera un fichero `client_secrets.json` dentro de la carpeta `/app/data`. El fichero debe tener este formato:

```json
{
    "web": {
        "client_id": "",
        "client_secret": "",
        "auth_uri": "",
        "token_uri": "",
        "userinfo_uri": "",
        "issuer": "",
        "redirect_uris": ["http://localhost:3000/oidc/authorize"]
    }
}
```

---
Proyecto desarrollado por:
- @aLVaRoZz01
- @oscarlpujol
- @pablofl01
---
<div align="center">
  Grupo GIROS &copy; 2026
</div>
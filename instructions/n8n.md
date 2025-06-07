# **Docker + n8n con datos en Disco Local D**


## 1. Cambiar ubicación de datos Docker a Disco Local D con Symlink

### Pasos:

1. **Cerrar Docker Desktop** y apagar WSL:
   ```powershell
   wsl --shutdown
    ```

2. **Mover datos actuales de Docker** (ubicados típicamente en C:\Users\<USER>\AppData\Local\Docker\wsl\disk) a disco D, por ejemplo:

    ```powershell
    Move-Item "$env:LOCALAPPDATA\Docker\wsl\disk" "D:\Docker\wsl\disk_backup"
    ```

3. **Crear enlace simbólico (symlink) desde la ruta original a la nueva ubicación:**

    ```powershell
    New-Item -ItemType Junction -Path "$env:LOCALAPPDATA\Docker\wsl\disk" -Target "D:\Docker\wsl\disk"
    ```

4. **Verificar permisos:**
    - Asegúrate que tu usuario tenga control total en la carpeta D:\Docker\wsl\disk
    - Verifica que no haya bloqueos por antivirus o seguridad de Windows (Ejecuta como Administrador si es necesario).

5. **Reiniciar Docker Desktop.**

    Verificar que Docker corre con datos en D:

    ```powershell
    docker info
    ```

    Revisa que no haya errores de acceso y que los contenedores funcionen normalmente.

## 2. Instalar n8n con Docker en disco D usando docker-compose.yaml
**Ejemplo básico docker-compose.yaml para n8n:**

```yaml
version: "3"

services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"    # Puerto para acceder a n8n en el navegador
    volumes:
      - d_n8n_data:/home/node/.n8n  # Monta volumen para persistir datos
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true          # Activa autenticación básica
      - N8N_BASIC_AUTH_USER=user            # Usuario para login
      - N8N_BASIC_AUTH_PASSWORD=password    # Contraseña para login
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http

volumes:
  d_n8n_data:
    driver: local
    driver_opts:
      type: none
      device: D:/AppData/n8n/data
      o: bind
```

**Pasos para correr:**
1. Guarda el archivo docker-compose.yaml en una carpeta, por ejemplo D:\n8n\.
2. Abre PowerShell o CMD en esa carpeta:
    ```powershell
    docker-compose up -d
    ```

3. Accede a n8n en:
`http://localhost:5678`

## 3. Observaciones importantes sobre permisos y credenciales
## Permisos:
La carpeta `D:\n8n\data` debe tener permisos de lectura y escritura para el usuario que corre Docker Desktop (normalmente tu usuario).

### Credenciales:
- La autenticación básica se activa con las variables `N8N_BASIC_AUTH_ACTIVE`, `N8N_BASIC_AUTH_USER`, y `N8N_BASIC_AUTH_PASSWORD`.

- Puedes cambiar estas credenciales en el archivo `docker-compose.yaml` y reiniciar el contenedor con:
    ```powershell
    docker-compose down
    docker-compose up -d
    ```

### Primer acceso a n8n:
- Después de iniciar sesión, se recomienda crear workflows iniciales o importar templates.
- La interfaz web permite gestionar credenciales para APIs y servicios externos.

## 4. Consejos para asegurar instalación correcta
- Ejecuta PowerShell o CMD como administrador cuando crees enlaces simbólicos o modifiques carpetas protegidas.

- Siempre haz backup de tus datos antes de mover carpetas o crear symlinks.

- Verifica que Docker Desktop está usando WSL2 como backend (en configuraciones de Docker Desktop).

- Para problemas de acceso a archivos VHDX, asegúrate que no haya procesos bloqueando los archivos y que el antivirus no interfiera.

- Si usas proxy, verifica la configuración de Docker para que tenga acceso a Internet.

## Referencias útiles
- Documentación oficial Docker Desktop (Windows & WSL2):
https://docs.docker.com/desktop/windows/wsl/

- Cómo mover la data de Docker Desktop a otro disco usando symlinks:
https://docs.docker.com/docker-for-windows/faqs/#how-do-i-move-docker-desktop-data-to-another-drive

- Documentación oficial Docker Compose (volúmenes y bind mounts):
https://docs.docker.com/compose/compose-file/compose-file-v3/#volumes

- n8n Documentation - Docker deployment:
https://docs.n8n.io/getting-started/installation/docker/

- n8n Environment Variables - Authentication and configuration:
https://docs.n8n.io/reference/environment-variables.html#basic-authentication

- WSL2 common troubleshooting:
https://learn.microsoft.com/en-us/windows/wsl/troubleshooting


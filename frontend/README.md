# Identylog Frontend

Esta carpeta contiene un frontend ligero creado con Vite + React para enlazar con las rutas del backend Django.

## Uso

1. Instala dependencias:

```bash
cd frontend
npm install
```

2. Inicia el servidor de desarrollo:

```bash
npm run dev
```

3. Abre el navegador en la URL que indique Vite.

## Rutas del backend utilizadas

- `/` → página de bienvenida
- `/registro/` → registro de usuario
- `/login/` → inicio de sesión
- `/dashboard/` → panel de usuario
- `/t/:token/` → página pública del soporte NFC
- `/activar/:token/` → activación de soporte NFC

El backend ya tiene CORS habilitado para desarrollo, por lo que puedes usar esta app separada desde un origen distinto.

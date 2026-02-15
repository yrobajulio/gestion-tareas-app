# 🚀 Guía de Deployment - Fase 2

## Sistema con Login + Supabase + Streamlit Cloud

---

## 📋 PARTE 1: Configurar Supabase (Base de Datos en la Nube)

### Paso 1.1: Crear cuenta en Supabase

1. Ve a https://supabase.com
2. Click en "Start your project"
3. Regístrate con GitHub (recomendado) o email
4. Es **100% GRATIS** para el plan que necesitas

### Paso 1.2: Crear proyecto

1. Click en "New Project"
2. Completa:
   - **Name**: `gestion-tareas` (o el nombre que quieras)
   - **Database Password**: Genera una contraseña segura (guárdala)
   - **Region**: South America (Brazil) - el más cercano a Chile
   - **Pricing Plan**: Free (está seleccionado por defecto)
3. Click "Create new project"
4. **Espera 2-3 minutos** mientras se crea tu base de datos

### Paso 1.3: Crear tabla de tareas

1. En el menú izquierdo, click en "Table Editor"
2. Click en "Create a new table"
3. Completa:
   - **Name**: `tareas`
   - Deja marcado "Enable Row Level Security (RLS)"
4. Agrega las siguientes columnas (click en "Add column"):

| Column Name     | Type                 | Default Value     | Nullable |
|-----------------|----------------------|-------------------|----------|
| id              | int8                 | Auto-increment    | No       |
| descripcion     | text                 | -                 | No       |
| fecha_objetivo  | date                 | -                 | No       |
| estado          | text                 | -                 | No       |
| autor           | text                 | -                 | No       |
| asignado        | text                 | -                 | No       |
| cliente         | text                 | -                 | No       |
| comentarios     | text                 | '[]'              | Yes      |
| created_at      | timestamptz          | now()             | Yes      |

5. Marca `id` como **Primary Key**
6. Click "Save"

### Paso 1.4: Configurar políticas de seguridad (RLS)

1. En la tabla `tareas`, click en el ícono de candado (RLS)
2. Click "New Policy"
3. Selecciona "Get started quickly" → "Enable read access to everyone"
4. Repite para crear otra política: "Enable insert access to everyone"
5. Repite para crear otra política: "Enable update access to everyone"
6. Repite para crear otra política: "Enable delete access to everyone"

**Nota**: En producción real deberías configurar políticas más restrictivas, pero para este proyecto funcional esto es suficiente.

### Paso 1.5: Obtener credenciales

1. En el menú izquierdo, click en "Settings" (⚙️)
2. Click en "API"
3. Copia y guarda estos dos valores:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon/public key**: `eyJhbGciOi....` (una clave larga)

**¡Guarda estas credenciales! Las necesitarás más adelante.**

### Paso 1.6: Insertar datos de ejemplo (opcional)

1. Ve a "Table Editor" → tabla `tareas`
2. Click "Insert" → "Insert row"
3. Agrega algunas tareas de ejemplo:

```
descripcion: "Revisión contrato anual"
fecha_objetivo: 2025-02-17
estado: "Pendiente"
autor: "Gerente de Proyectos"
asignado: "Julio Yroba"
cliente: "Innova SA"
comentarios: []
```

---

## 📋 PARTE 2: Subir código a GitHub

### Paso 2.1: Crear repositorio en GitHub

1. Ve a https://github.com
2. Click en el botón "+" arriba a la derecha → "New repository"
3. Completa:
   - **Repository name**: `gestion-tareas-app`
   - **Description**: "Sistema de gestión de tareas con Streamlit"
   - Marca "Public" (o Private si prefieres)
   - **NO** marques "Add a README file"
4. Click "Create repository"

### Paso 2.2: Subir archivos

Tienes dos opciones:

#### Opción A: Usar GitHub Web (más fácil)

1. En tu repositorio recién creado, click "uploading an existing file"
2. Arrastra estos archivos:
   - `app.py`
   - `requirements.txt`
   - `.gitignore`
3. En el mensaje de commit escribe: "Initial commit - Fase 2"
4. Click "Commit changes"

#### Opción B: Usar Git desde terminal

```bash
# En tu carpeta local con los archivos
git init
git add app.py requirements.txt .gitignore
git commit -m "Initial commit - Fase 2"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/gestion-tareas-app.git
git push -u origin main
```

**✅ Verifica**: Deberías ver tus 3 archivos en GitHub

---

## 📋 PARTE 3: Deploy en Streamlit Cloud

### Paso 3.1: Crear cuenta en Streamlit Cloud

1. Ve a https://share.streamlit.io
2. Click "Sign up" o "Get started"
3. Conecta con tu cuenta de GitHub
4. Autoriza el acceso a Streamlit

### Paso 3.2: Crear nueva app

1. Click "New app" (botón azul)
2. Completa:
   - **Repository**: Selecciona `gestion-tareas-app`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: Elige un nombre único (ej: `gestion-tareas-tuempresa`)
3. **NO HAGAS CLICK EN DEPLOY TODAVÍA**

### Paso 3.3: Configurar Secrets (IMPORTANTE)

1. Click en "Advanced settings"
2. En la sección "Secrets", pega lo siguiente (usa TUS credenciales de Supabase):

```toml
[supabase]
url = "https://xxxxx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."
```

**Reemplaza**:
- `url` con tu Project URL de Supabase
- `key` con tu anon/public key de Supabase

3. Click "Save"

### Paso 3.4: Deploy!

1. Click "Deploy"
2. Espera 2-3 minutos mientras se instala todo
3. Si todo está bien, verás tu app funcionando! 🎉

---

## 📋 PARTE 4: Probar la aplicación

### Paso 4.1: Acceder a la app

Tu app estará disponible en:
```
https://gestion-tareas-tuempresa.streamlit.app
```

### Paso 4.2: Usuarios de prueba

Inicia sesión con cualquiera de estos usuarios:

**Jefes de Proyecto:**
- Usuario: `julio.yroba` / Password: `jefe123`
- Usuario: `jose.quintero` / Password: `jefe123`
- Usuario: `matias.riquelme` / Password: `jefe123`

**Gerentes:**
- Usuario: `gerente.proyectos` / Password: `gerente123`
- Usuario: `gerente.general` / Password: `admin123`

### Paso 4.3: Verificar funcionalidades

✅ **Como Jefe de Proyecto:**
- Ver Dashboard Gerencia
- Ver solo tus tareas asignadas
- Crear tareas (autor = tu nombre automáticamente)
- Editar tus tareas
- Cambiar estado
- Agregar comentarios
- ❌ NO puedes eliminar tareas

✅ **Como Gerente:**
- Ver Dashboard Gerencia completo
- Ver todas las tareas
- Crear tareas para cualquiera
- Editar cualquier tarea
- Eliminar tareas
- Exportar reportes

---

## 🔧 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'supabase'"

**Solución**: Verifica que `requirements.txt` esté en tu repositorio con `supabase==2.3.4`

### Error: "Error conectando a Supabase"

**Solución**: 
1. Revisa que los secrets estén bien configurados
2. Verifica que copiaste bien la URL y la key (sin espacios extras)
3. Ve a Streamlit Cloud → Settings → Secrets y verifica

### La tabla no se crea o da error

**Solución**:
1. Ve a Supabase → Table Editor
2. Verifica que la tabla `tareas` exista
3. Verifica que las columnas tengan los tipos correctos
4. Verifica que RLS esté habilitado con políticas

### No puedo ver mis tareas

**Solución**:
1. Ve a Supabase → Table Editor → tareas
2. Verifica que haya datos
3. Inserta una tarea de prueba manualmente
4. Refresca la app en Streamlit

---

## 🔐 Cambiar Contraseñas (Producción)

Para cambiar las contraseñas después de deployment:

1. Edita `app.py` en GitHub
2. Cambia las contraseñas en el diccionario `USUARIOS`
3. Commit los cambios
4. Streamlit Cloud automáticamente re-deployará

**Importante**: Las contraseñas están en texto plano por simplicidad. Para producción real deberías usar hashing (bcrypt, etc).

---

## 📊 Resumen de Permisos

| Funcionalidad                | Jefe Proyecto | Gerente |
|------------------------------|---------------|---------|
| Ver Dashboard Gerencia       | ✅            | ✅      |
| Ver sus tareas               | ✅            | ✅      |
| Ver tareas de otros          | ❌            | ✅      |
| Crear tareas                 | ✅            | ✅      |
| Editar sus tareas            | ✅            | ✅      |
| Editar tareas de otros       | ❌            | ✅      |
| Eliminar tareas              | ❌            | ✅      |
| Cambiar estado               | ✅ (propias)  | ✅      |
| Agregar comentarios          | ✅            | ✅      |
| Exportar reportes            | ✅            | ✅      |
| Autor se llena automático    | ✅            | ✅      |

---

## 🎯 Próximos Pasos (Mejoras Futuras)

1. **Notificaciones por email** cuando se asigna una tarea
2. **Cambio de contraseña** desde la app
3. **Registro de usuarios** (solo admin)
4. **Logs de auditoría** (quién modificó qué)
5. **Adjuntar archivos** a las tareas
6. **Gráficos de productividad** por persona
7. **Exportar a PDF** con formato
8. **Filtros avanzados** en el dashboard
9. **Vista calendario**
10. **Integración con Slack/Teams**

---

## 📞 Soporte

Si tienes problemas:

1. **Revisa los logs**: En Streamlit Cloud → Manage app → Logs
2. **Verifica Supabase**: Table Editor para ver datos
3. **Prueba local**: Crea `.streamlit/secrets.toml` con tus credenciales y ejecuta `streamlit run app.py`

---

## ✅ Checklist Final

- [ ] Cuenta Supabase creada
- [ ] Tabla `tareas` configurada con columnas correctas
- [ ] Políticas RLS activadas
- [ ] Credenciales de Supabase guardadas
- [ ] Repositorio GitHub creado
- [ ] Archivos subidos a GitHub
- [ ] App creada en Streamlit Cloud
- [ ] Secrets configurados correctamente
- [ ] App deployada exitosamente
- [ ] Probado login con los 5 usuarios
- [ ] Verificado que se guardan tareas en Supabase

---

## 🎉 ¡Listo!

Tu sistema está en producción y accesible desde cualquier lugar del mundo.

**URL de tu app**: https://TU-APP.streamlit.app

¡Disfruta tu sistema de gestión de tareas! 🚀

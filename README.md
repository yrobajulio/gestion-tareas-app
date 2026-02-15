# 📋 Sistema de Gestión de Tareas Empresarial

Sistema web de gestión de tareas con autenticación, roles de usuario y persistencia en la nube usando Streamlit + Supabase.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red.svg)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green.svg)

---

## 🌟 Características

### ✨ Funcionalidades Principales

- **Sistema de Login** con 5 usuarios predefinidos
- **Roles diferenciados**: Jefes de Proyecto y Gerencia
- **Dashboard Gerencial** con métricas en tiempo real
- **Gestión de tareas** con estados (Pendiente, En Proceso, Completada)
- **Sistema de comentarios** en cada tarea
- **Exportación de datos** a CSV y Excel
- **Base de datos en la nube** con Supabase (PostgreSQL)
- **Persistencia automática** de todos los cambios
- **Diseño responsive** para móviles y escritorio

### 👥 Usuarios del Sistema

**Jefes de Proyecto** (3 usuarios):
- Julio Yroba
- José Quintero
- Matías Riquelme

**Gerencia** (2 usuarios):
- Gerente de Proyectos
- Gerente General

### 🔐 Permisos por Rol

| Funcionalidad | Jefe Proyecto | Gerente |
|---------------|---------------|---------|
| Ver Dashboard Gerencia | ✅ | ✅ |
| Crear tareas | ✅ | ✅ |
| Editar sus tareas | ✅ | ✅ |
| Editar tareas de otros | ❌ | ✅ |
| Eliminar tareas | ❌ | ✅ |
| Autor automático | ✅ | ✅ |

---

## 🚀 Deployment en Producción

### Opción 1: Streamlit Cloud (Recomendado)

**Requisitos previos:**
- Cuenta en GitHub
- Cuenta en Supabase (gratis)
- Cuenta en Streamlit Cloud (gratis)

**Pasos rápidos:**
1. Configura Supabase (ver `GUIA_DEPLOYMENT.md`)
2. Sube el código a GitHub
3. Conecta Streamlit Cloud con tu repo
4. Configura los secrets (credenciales de Supabase)
5. ¡Deploy!

📖 **Guía completa paso a paso**: Ver archivo `GUIA_DEPLOYMENT.md`

### Opción 2: Ejecución Local

```bash
# 1. Clonar repositorio
git clone https://github.com/TU-USUARIO/gestion-tareas-app.git
cd gestion-tareas-app

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar Supabase
# Crear archivo .streamlit/secrets.toml con:
[supabase]
url = "https://xxxxx.supabase.co"
key = "tu-anon-key"

# 4. Ejecutar
streamlit run app.py
```

---

## 📊 Estructura del Proyecto

```
gestion-tareas-app/
├── app.py                          # Aplicación principal
├── requirements.txt                # Dependencias Python
├── .gitignore                      # Archivos ignorados por Git
├── README.md                       # Este archivo
├── GUIA_DEPLOYMENT.md             # Guía paso a paso de deployment
├── setup_supabase.sql             # Script SQL para crear tabla
└── .streamlit/
    └── secrets.toml.example       # Ejemplo de configuración
```

---

## 🗄️ Esquema de Base de Datos

### Tabla: `tareas`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BIGSERIAL | ID único (auto-incrementa) |
| descripcion | TEXT | Descripción de la tarea |
| fecha_objetivo | DATE | Fecha límite |
| estado | TEXT | Pendiente/En Proceso/Completada |
| autor | TEXT | Quién creó la tarea |
| asignado | TEXT | A quién está asignada |
| cliente | TEXT | Nombre del cliente |
| comentarios | TEXT | JSON con historial de comentarios |
| created_at | TIMESTAMPTZ | Fecha de creación |
| updated_at | TIMESTAMPTZ | Última actualización |

---

## 💻 Tecnologías Utilizadas

- **Frontend**: Streamlit (Python)
- **Base de Datos**: Supabase (PostgreSQL)
- **Visualización**: Altair, Pandas
- **Export**: OpenPyXL (Excel)
- **Hosting**: Streamlit Cloud

---

## 🎨 Capturas de Pantalla

### Página de Login
- Formulario de autenticación
- Lista de usuarios de prueba

### Dashboard Gerencia
- Métricas semanales
- Tareas por persona
- Gráficos de estado
- Alertas de atrasos

### Vista Jefe de Proyecto
- Crear tareas
- Filtrar y buscar
- Editar tareas asignadas
- Sistema de comentarios

---

## 🔑 Credenciales de Prueba

### Jefes de Proyecto
```
Usuario: julio.yroba
Password: jefe123

Usuario: jose.quintero
Password: jefe123

Usuario: matias.riquelme
Password: jefe123
```

### Gerencia
```
Usuario: gerente.proyectos
Password: gerente123

Usuario: gerente.general
Password: admin123
```

---

## 🛠️ Desarrollo Local

### Requisitos
- Python 3.9 o superior
- pip

### Instalación

```bash
# Clonar repositorio
git clone <tu-repo>
cd gestion-tareas-app

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar secrets
# Crear archivo .streamlit/secrets.toml con credenciales de Supabase

# Ejecutar
streamlit run app.py
```

### Configuración de Supabase para desarrollo

1. Crear proyecto en https://supabase.com
2. Ejecutar el script `setup_supabase.sql` en SQL Editor
3. Copiar URL y anon key a `.streamlit/secrets.toml`

---

## 📝 Changelog

### Fase 2 (Actual)
- ✅ Sistema de autenticación con 5 usuarios
- ✅ Roles y permisos diferenciados
- ✅ Integración con Supabase
- ✅ Persistencia en la nube
- ✅ Autor automático según usuario logueado
- ✅ Dashboard accesible para todos
- ✅ Jefes de proyecto ven el dashboard

### Fase 1 (Completada)
- ✅ Dashboard gerencial con métricas
- ✅ Vistas por jefe de proyecto
- ✅ Sistema de comentarios
- ✅ Edición de tareas
- ✅ Filtros y búsqueda
- ✅ Exportación CSV/Excel
- ✅ Validaciones y confirmaciones
- ✅ Diseño responsive

---

## 🚧 Roadmap (Futuras Mejoras)

### Corto Plazo
- [ ] Cambio de contraseña desde la app
- [ ] Recuperación de contraseña por email
- [ ] Notificaciones de tareas próximas a vencer

### Mediano Plazo
- [ ] Adjuntar archivos a las tareas
- [ ] Logs de auditoría (historial de cambios)
- [ ] Vista de calendario
- [ ] Gráficos de productividad por persona

### Largo Plazo
- [ ] Integración con Slack/Teams
- [ ] App móvil nativa
- [ ] API REST para integraciones
- [ ] Dashboard personalizable

---

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'supabase'"
**Solución**: Instala las dependencias con `pip install -r requirements.txt`

### Error: "Error conectando a Supabase"
**Solución**: Verifica que el archivo `.streamlit/secrets.toml` tenga las credenciales correctas

### No se guardan las tareas
**Solución**: 
1. Verifica conexión a Supabase
2. Revisa que la tabla `tareas` exista
3. Verifica que RLS esté configurado correctamente

---

## 👨‍💻 Autor

Desarrollado para gestión empresarial de tareas y proyectos.

---

## 📄 Licencia

Este proyecto es privado y de uso interno empresarial.

---

## 🤝 Contribuciones

Para sugerir mejoras o reportar bugs:
1. Abre un Issue en GitHub
2. Describe el problema o mejora
3. Si es un bug, incluye pasos para reproducirlo

---

## 📞 Soporte

Para soporte técnico o preguntas:
- Revisa la `GUIA_DEPLOYMENT.md`
- Consulta los logs en Streamlit Cloud
- Verifica los datos en Supabase Table Editor

---

## ⭐ Agradecimientos

- Streamlit por el framework
- Supabase por la base de datos
- Altair por las visualizaciones

---

**¡Disfruta del sistema! 🎉**

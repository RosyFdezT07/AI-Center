# 🧠 Planificador Inteligente de Eventos - Centro de Investigación en IA

https://img.shields.io/badge/Python-3.9+-blue   🐍 Python 3.9+     
https://img.shields.io/badge/Streamlit-1.28+-FF4B4B  🎨Streamlit  
https://img.shields.io/badge/Licencia-MIT-green  📜 MIT License  

Sistema profesional de planificación de eventos con recursos limitados

# *Tabla de Contenidos*

🎯 Descripción del Proyecto

🏛️ Dominio Elegido

✨ Características Principales

🏗️ Arquitectura del Sistema

🚀 Instalación Rápida

📊 Guía de Uso

🔧 Estructura del Proyecto

📄 Entregables

🏆 Desafíos Opcionales

# *🎯 Descripción del Proyecto*

El Planificador Inteligente de Eventos es una solución completa desarrollada para la gestión optimizada de recursos altamente especializados en centros de investigación de Inteligencia Artificial. Este sistema resuelve uno de los problemas más críticos en entornos académicos y de investigación: la asignación eficiente de recursos limitados y costosos a múltiples proyectos que compiten por ellos en el tiempo. El sistema garantiza que:

• Ningún recurso se asigne a más de un evento simultáneamente

• Se respeten reglas de negocio complejas (restricciones personalizadas)

• La planificación sea óptima y eficiente con búsqueda automática de huecos

# *🏛️ Dominio Elegido:* 

**Centro de Investigación en IA**

Contexto del Dominio

En un centro de investigación de IA de alto nivel, los recursos son costosos, especializados y limitados. La planificación incorrecta puede:

• Costar miles de dólares en tiempo de GPU desperdiciado

• Violar normativas de seguridad con datos sensibles

• Retrasar proyectos críticos por conflictos de recursos

*Recursos Modelados*

💻 Recursos Computacionales

Cluster GPU A100 - 8x NVIDIA A100, 320GB, $500K

Cluster GPU V100 - 4x NVIDIA V100, 128GB, $250K

Servidor CPU High-Memory - 1TB RAM, 128 núcleos

Estación de Trabajo RTX 4090 - 4 unidades disponibles

👨‍🔬 Recursos Humanos

Investigador Senior - Visión Computacional - 5+ años experiencia

Investigador Senior - NLP - Especialista en Large Language Models

Ingeniero de MLOps - DevOps para Machine Learning

Científico de Datos - Análisis estadístico avanzado

🏢 Espacios

Laboratorio de Datos Sensibles - Nivel 3 seguridad, HIPAA/GDPR

Sala de Servidores - Temperatura controlada, UPS redundante

Sala de Reuniones Principal - Capacidad 12 personas, proyector 4K

Laboratorio de Prototipado - Impresoras 3D, sensores IoT

*⚖️ Restricciones Implementadas*

1.Co-requisitos (INCLUSIÓN)

    "Recurso A requiere Recurso B"

• Ejemplo 1: Cluster GPU requiere Investigador Especializado

RestriccionCoRequisito(
    principal="cluster_gpu_a100",
    requerido="investigador_vision"
)

Justificación de negocio: Un cluster de $500K sin experto es hardware subutilizado y riesgoso.

• Ejemplo 2: Laboratorio de datos sensibles requiere Científico de Datos

RestriccionCoRequisito(
    principal="lab_datos_sensibles",
    requerido="cientifico_datos"
)

Justificación de seguridad: Datos médicos requieren supervisión especializada.

2.Exclusiones Mutuas (EXCLUSIÓN)

    "Recurso A NO puede usarse con Recurso B"

• Ejemplo 1: Datos sensibles NO en cloud público

RestriccionExclusionMutua(
    recurso_a="lab_datos_sensibles",
    recurso_b="servidor_externo"
)

Justificación de seguridad: Cumplimiento de normas para datos médicos/gubernamentales.

• Ejemplo 2: No mezclar clusters GPU grandes

RestriccionExclusionMutua(
    recurso_a="cluster_gpu_a100",
    recurso_b="cluster_gpu_v100"
)

Justificación técnica: Limitación de infraestructura eléctrica y refrigeración.

3.Límites de Capacidad

    "Máximo X recursos por categoría"

• Ejemplo: Máximo 4 personas por evento

RestriccionCapacidad(
    tipo_recurso="humano",
    capacidad_maxima=4
)

Justificación organizacional: Grupos pequeños son más eficientes

# *✨ Características Principales:*

*🧠 Planificación Inteligente*

• Validación en tiempo real de conflictos y restricciones

• Búsqueda automática de huecos en los próximos 7 días

• Priorización inteligente de eventos (1-5 estrellas)

*🔍 Gestión Avanzada*

• Dashboard interactivo con métricas en tiempo real

• Agenda por recurso visualización tipo timeline

• Filtros múltiples por tipo, estado, fecha

• Exportación/Importación completa del estado del sistema

*🛡️ Robustez* 

• Persistencia completa con sistema de backup automático

• Manejo de errores con mensajes claros al usuario

• Migración automática de formatos antiguos

• Validación exhaustiva de todos los datos de entrada

# *🏗️ Arquitectura del Sistema:*

*Diagrama de Arquitectura*

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFAZ WEB (Streamlit)                 │
├─────────────────────────────────────────────────────────────┤
│                    APLICACIÓN (Casos de Uso)                │
│  • Planificador (Orquestador principal)                     │
│  • Validación de reglas de negocio                          │
├─────────────────────────────────────────────────────────────┤
│                    DOMINIO (Entidades/Reglas)               │
│  • Eventos (con duración, recursos, prioridad)              │
│  • Recursos (computacionales, humanos, espacios)            │
│  • Restricciones (co-requisitos, exclusiones, capacidad)    │
├─────────────────────────────────────────────────────────────┤
│                    INFRAESTRUCTURA (Persistencia)           │
│  • Sistema de archivos JSON                                 │
│  • Serialización/Deserialización                            │
│  • Backup automático con timestamp                          │
└─────────────────────────────────────────────────────────────┘
```


# *🚀 Instalación Rápida:*

*Prerrequisitos*

Python 3.9 o superior

pip (gestor de paquetes de Python)

500MB de espacio libre

*Instalación en 3 Pasos*

**1. Clonar el repositorio**
git clone https://github.com/RosyFdezT07/AI-Center 
cd AI-Center

**2. Crear entorno virtual** (recomendado)
python -m venv venv

*En Windows:*
venv\Scripts\activate

*En Linux/Mac:*
source venv/bin/activate

**3. Instalar dependencias**
pip install -r requirements.txt

*Verificar Instalación*

python -c "import streamlit; print('✅ Streamlit instalado')"

python -c "import pandas; print('✅ Pandas instalado')"

python -c "import plotly; print('✅ Plotly instalado')"

# *📊 Guía de Uso:*

*Iniciar la Aplicación*

```bash
python main.py
```
Nota: Este comando iniciará automáticamente el servidor de Streamlit a través de nuestro script puente

*La aplicación se abrirá inmediatamente en http://localhost:8501

🖥️ Pantallas Principales

1. 📊 Dashboard Principal

• Métricas clave: Recursos, eventos, ocupación

• Eventos próximos: Próximos 7 días

2. 📅 Gestión de Eventos

• Visualización de todos los eventos creados

• Filtrar por estado y tipo

3. 🔧 Gestión de Recursos

• Inventario completo: Ver todos los recursos disponibles

• Agenda por recurso: Timeline de uso específico

• Estadísticas

4. ✨ Nuevo Evento

**Ejemplo: Planificar nuevo evento**
1. Nombre: "Entrenamiento Modelo Detección Cáncer"
2. Fecha de inicio: 05/01/2026 
3. Hora de inicio: 14:00
4. Fecha de fin: 05/01/2026
5. Hora de fin: 18:00
6. Recursos: Cluster GPU A100 + Investigador Visión
7. Prioridad: ⭐⭐⭐⭐⭐ (Crítico)

5. 🔍 Búsqueda de Huecos

• Parámetros: Duración, recursos necesarios, rango de fechas

• Algoritmo: Búsqueda inteligente con saltos de 10 minutos

• Resultados: Visualización de los próximos 10 huecos disponibles


6. 💾 Gestión de Datos
• Guardar/cargar estado del sistema
• Sistema de backup automático
• Limpieza de eventos antiguos

*Flujo de Trabajo Típico*

Investigador necesita recursos específicos

Sistema verifica disponibilidad inmediata

Si hay conflicto, busca hueco automáticamente

Sistema confirma y guarda planificación

# *🔧 Estructura del Proyecto:*

```
AI-Center/
│
├── core/                    
# Interfaces y tipos base
│   ├── __init__.py
│   ├── interfaces.py       
# Protocolos para dependencias
│   └── tipos.py           
# Type hints y tipos de datos
│
├── dominio/                
# Entidades y reglas de negocio
│   ├── __init__.py
│   ├── recursos.py        
# Recurso, GestorRecursos
│   ├── eventos.py         
# Evento, GestorEventos
│   └── restricciones.py   
# Sistema completo de restricciones
│
├── aplicacion/            
# Casos de uso y lógica
│   ├── __init__.py
│   └── planificador.py   
# Clase principal Planificador
│
├── infraestructura/       
# Persistencia y servicios
│   ├── __init__.py
│   └── persistencia.py   
# Guardar/cargar sistema completo
│
├── datos/                 
# Datos del sistema
│   ├── datos.json 
# Estado actual (formato nuevo)
│   
├── app.py                
# Interfaz web Streamlit
├──main.py
# Script puente
├── requirements.txt      
# Dependencias
├── README.md            
# Este archivo
└── backups/          
# Backups automáticos
└── .gitignore
└──  __init__.py
```

*📚 Explicación de Módulos Clave*

dominio/restricciones.py - Cerebro del Sistema

Implementa 3 tipos de restricciones:

    RestriccionCoRequisito: "A requiere B"

    RestriccionExclusionMutua: "A NO con B"

    RestriccionCapacidad: "Máximo X de tipo Y"

aplicacion/planificador.py - Orquestador Principal

    class Planificador:

        def planificar_evento(...)      
        # Validación completa
        def verificar_conflictos(...)    
        # Algoritmo eficiente
        def buscar_hueco_automático(...) 
        # Búsqueda inteligente
        def guardar_datos(...)        
        # Persistencia delegada

infraestructura/persistencia.py - Gestor de Estado

    class Persistencia:
        @staticmethod
        def guardar_sistema(...)    
        # Guarda TODO el estado
        @staticmethod  
        def cargar_sistema(...)     
        # Carga con referencias intactas
        @staticmethod
        def crear_backup(...)      
         # Backup con timestamp

# *📄 Entregables*

1. Código Fuente

    -> Archivos Python organizados por responsabilidad

    -> Comentarios detallados en español

    -> Type hints completos para mejor mantenibilidad

    -> Manejo de errores robusto en toda la aplicación

2. Documentación (README.md)

    -> Dominio elegido y justificación (Centro de Investigación IA)

    -> Descripción detallada de eventos, recursos y restricciones

    -> Ejemplos concretos de cada restricción implementada

    -> Instrucciones claras de instalación y uso

    -> Explicación de arquitectura y decisiones técnicas

3. Archivo de Datos de Ejemplo

    -> datos.json - Ejemplo completo funcionamiento

    -> Recursos realistas del dominio elegido

    -> Eventos de ejemplo que demuestran todas las funcionalidades

    -> Restricciones configuradas que muestran la lógica del sistema

# *🏆 Desafíos Opcionales Implementados:*

1. Recursos con Cantidad (Pools de Recursos)
class Recurso:
    def __init__(self, capacidad: int = 1):
        self.capacidad = capacidad  # Número de unidades disponibles

Implementado en: Recurso.capacidad y algoritmo de verificación en planificador.py

2. Interfaz Gráfica (Streamlit)

 Dashboard interactivo con métricas en tiempo real

 Visualización timeline de eventos por recurso

 Filtros avanzados combinados (tipo, estado, fecha)

 Formularios inteligentes con validación en tiempo real

 Sistema de temas personalizado

3. Funcionalidades Adicionales

 Búsqueda de huecos inteligente con algoritmo optimizado

 Sistema de prioridades (1-5 estrellas)

 Estados de evento (planificado, en curso, completado, cancelado)

 Sistema de backup automático 


Este sistema está listo para ser desplegado en cualquier centro de investigación que necesite gestionar recursos valiosos y especializados de manera inteligente y eficiente.

Desarrollado para el curso de Ciencias de la Computación 1er año
Centro de Investigación en IA - Planificador Inteligente de Eventos
📅 Enero 2026 • 🐍 Python 3.9+ • 🎨 Streamlit




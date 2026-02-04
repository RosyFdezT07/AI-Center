# Informe Técnico: Planificador Inteligente de Eventos para Centro de Investigación en IA

## 1. Introducción

El proyecto consiste en un sistema de planificación de eventos diseñado específicamente para un centro de investigación en Inteligencia Artificial. Se seleccionó este dominio por su complejidad inherente: combina recursos extremadamente costosos (clusters GPU de cientos de miles de dólares), restricciones de seguridad reales, y una necesidad crítica de optimización debido a la alta competencia por recursos limitados. La aplicación resuelve el problema fundamental de asignar estos recursos especializados a eventos que compiten por ellos en el tiempo, garantizando que no se produzcan conflictos y que se respeten las reglas de negocio.

### *1.1 Dominio de Aplicación*

Un centro de investigación en IA presenta desafíos únicos de planificación. Los recursos no son meros activos físicos, sino instrumentos especializados con interdependencias complejas. Por ejemplo, un cluster GPU de última generación no es útil sin investigadores especializados que lo operen, y ciertos experimentos con datos sensibles requieren espacios físicos con certificaciones específicas de seguridad. Este nivel de complejidad hace que el dominio sea ideal para demostrar la capacidad del sistema para manejar restricciones multidimensionales.

### *1.2 Tipos de Eventos Gestionados*

El sistema maneja seis categorías principales de eventos, cada una con características temporales y de recursos distintas:
- **Entrenamiento de modelos**: Sesiones que pueden durar desde horas hasta días, consumiendo grandes cantidades de recursos computacionales
- **Procesamiento de datos**: Operaciones intensivas que requieren balance entre capacidad de cómputo y almacenamiento
- **Investigación**: Actividades experimentales con requisitos impredecibles de recursos
- **Reuniones**: Eventos de duración fija que consumen principalmente recursos humanos y espacios
- **Seminarios**: Eventos de divulgación 
- **Inferencia**: Ejecución de modelos pre-entrenados que puede programarse en lotes

### *1.3 Recursos del Sistema*

Los recursos se modelaron en tres grupos principales con atributos específicos que permiten validaciones complejas:

**Recursos Computacionales:**
- Clusters GPU (A100, V100) con atributos como memoria GPU, consumo energético y software preinstalado
- Servidores CPU de alta memoria con especificaciones de núcleos y RAM
- Estaciones de trabajo especializadas con capacidades de gráficos específicas

**Recursos Humanos:**
- Investigadores senior con atributos de especialización, años de experiencia y certificaciones
- Ingenieros de MLOps con habilidades específicas en plataformas cloud
- Científicos de datos con niveles de acceso a datos sensibles

**Espacios Físicos:**
- Laboratorios con requisitos de acceso
- Salas con control ambiental para equipos sensibles
- Espacios colaborativos

### *1.4 Restricciones Implementadas*

Las restricciones implementadas reflejan problemas reales de planificación en entornos de investigación:

**Restricciones de Co-requisito:**
Basadas en dependencias técnicas y regulatorias. Por ejemplo, un cluster GPU de $500,000 requiere un investigador certificado porque el mal uso podría dañar el equipo o generar resultados inválidos.

**Restricciones de Exclusión Mutua:**
Derivadas de limitaciones físicas y de seguridad. Por ejemplo, no se pueden ejecutar dos experimentos con altos requisitos energéticos simultáneamente porque sobrecargarían la infraestructura eléctrica del edificio.

**Restricciones de Capacidad:**
Originadas en consideraciones prácticas de gestión. Limitar el número de investigadores por evento asegura que las discusiones sean productivas y que la supervisión sea adecuada.

## 2. Estructura del Proyecto y Proceso de Diseño

### *2.1 Análisis y Diseño Previo*

Antes de escribir la primera línea de código, se realizó un proceso de diseño iterativo que incluyó:

1. **Modelado de dominio**: Se identificaron las entidades principales (Evento, Recurso) y sus relaciones mediante diagramas de clases iniciales. Este proceso reveló la necesidad de separar la "capacidad" de un recurso de su "existencia física", lo que llevó al diseño de recursos con atributo de capacidad.

2. **Definición de escenarios de uso**: Se escribieron 15 escenarios de uso específicos (ej: "Planificar entrenamiento de modelo CNN con datos médicos") que ayudaron a identificar requisitos funcionales y no funcionales.

3. **Evaluación de alternativas arquitectónicas**: Se consideraron varias arquitecturas posibles, seleccionándose la arquitectura por capas por su balance entre simplicidad y separación de responsabilidades.

4. **Diseño de algoritmos clave**: Especial atención se dedicó al algoritmo de detección de conflictos temporales, evaluándose dos aproximaciones (fuerza bruta y algoritmo de barrido de línea) seleccionándose este último por su eficiencia O(n log n).

### *2.2 Arquitectura Final*

El sistema se estructuró en cuatro capas siguiendo principios de Arquitectura Limpia:

**Capa Core**: Contiene definiciones de tipos e interfaces que actúan como contratos entre módulos. Esta decisión permitió desarrollar los módulos de Dominio y Aplicación de forma independiente, facilitando las pruebas unitarias. Los protocolos `IRecursoProtocol` e `IEventoProtocol` eliminan dependencias circulares permitiendo que, por ejemplo, el módulo de Restricciones pueda validar eventos sin conocer detalles de implementación.

**Capa Dominio**: Aquí reside el corazón del negocio. Se implementaron recursos, eventos y un sistema de restricciones, donde cada tipo de restricción es una estrategia concreta. 

**Capa de Aplicación**: La clase `Planificador` actúa como orquestador , proporcionando una interfaz simplificada a la complejidad subyacente. Se implementó el patrón Template Method en `planificar_evento()` donde los pasos de validación son fijos pero ciertas operaciones (como la búsqueda de huecos alternativos) pueden variar.

**Capa de Infraestructura**: La clase `Persistencia` implementa el patrón Memento, permitiendo guardar y restaurar el estado completo del sistema. Se eligió JSON sobre bases de datos SQL por su simplicidad y adecuación a la escala esperada (cientos, no miles, de eventos).

### **2.3 Decisiones de Diseño Clave y su Justificación**

**Modelado de Recursos con Capacidad**: En lugar de modelar cada estación de trabajo RTX 4090 como recurso individual, se optó por un recurso "Estación RTX 4090" con capacidad=4. Esta decisión redujo la complejidad de la interfaz de usuario (los usuarios seleccionan "cuántas" necesitan, no "cuáles específicamente") y simplificó la persistencia. La alternativa (recursos individuales) habría requerido nombrar cada estación (RTX_4090_01, RTX_4090_02) complicando innecesariamente la selección.

**Sistema de Restricciones Desacoplado**: Las restricciones se implementaron completamente separadas de la lógica temporal. Esta separación permite reutilizar el motor de restricciones en otros contextos (ej: validar combinaciones de recursos para presupuestos) y facilita las pruebas unitarias. La alternativa (integrar validación de restricciones en la verificación de conflictos) habría creado código difícil de mantener.

**Patrón de Búsqueda por Intervalos**: Para la búsqueda de huecos, se implementó un algoritmo que avanza en intervalos de 10 minutos en lugar de evaluar todos los posibles intervalos continuos. Esta decisión, aunque podría perder algunos huecos de duración no múltiplo de 10 minutos, redujo la complejidad computacional de O(n²) a O(n) para la búsqueda. En la práctica, la precisión de 10 minutos es suficiente para el dominio.

## **3. Desarrollo y Desafíos Técnicos**

### **3.1 Proceso de Desarrollo Iterativo**

El desarrollo siguió una metodología incremental con retrospectivas después de cada hito:

**Iteración 1 (2 semanas): Entidades básicas y gestores**
- Se implementaron `Recurso`, `Evento`, `GestorRecursos`, `GestorEventos`
- **Problema encontrado**: La comparación de fechas con zonas horarias causaba inconsistencias
- **Solución**: Se estandarizó en UTC para almacenamiento y se convirtió a hora local solo para visualización
- **Aprendizaje**: Las operaciones con datetime requieren un manejo consistente de timezone desde el inicio

**Iteración 2 (3 semanas): Sistema de restricciones y planificación básica**
- Se implementó la jerarquía de restricciones y el algoritmo de validación
- **Problema encontrado**: Las restricciones de capacidad no consideraban recursos con capacidad>1
- **Solución**: Se extendió la interfaz de restricciones para recibir no solo la lista de recursos sino también las cantidades solicitadas
- **Aprendizaje**: Las interfaces deben diseñarse pensando en extensibilidad futura

**Iteración 3 (2 semanas): Persistencia y recuperación de estado**
- Se implementó la serialización/deserialización completa
- **Problema encontrado**: Al cargar eventos, las referencias a recursos se perdían
- **Solución**: Se implementó un sistema de "reconstrucción de referencias" que primero carga todos los recursos en un diccionario por ID, luego los asigna a eventos
- **Aprendizaje**: La persistencia de grafos de objetos requiere estrategias específicas

**Iteración 4 (3 semanas): Interfaz de usuario y optimizaciones**
- Se desarrolló la interfaz Streamlit con dashboard y formularios
- **Problema encontrado**: La recarga completa de la página con cada interacción era lenta
- **Solución**: Se implementó uso intensivo de `st.session_state` para mantener estado entre interacciones
- **Aprendizaje**: Las aplicaciones web interactivas requieren gestión cuidadosa del estado del cliente

### **3.2 Problemas Técnicos Específicos y Soluciones**

**Problema 1: Algoritmo ineficiente para verificación de conflictos**
- **Situación inicial**: El método `verificar_conflictos()` comparaba el nuevo evento con todos los eventos existentes, complejidad O(n²). Con 100 eventos, requería 10,000 comparaciones.
- **Síntoma**: La planificación de eventos se volvía lenta (2-3 segundos) con más de 50 eventos programados.
- **Solución implementada**: Se aplicó el "algoritmo de barrido de línea" (line sweep algorithm):
  1. Para cada recurso, se crea una lista de puntos (tiempo, cambio) donde "cambio" es +cantidad al inicio de un evento y -cantidad al final
  2. Se ordenan estos puntos por tiempo (O(n log n))
  3. Se recorre una vez acumulando el uso actual (O(n))
  4. Si en algún punto el uso excede la capacidad, hay conflicto
- **Resultado**: La complejidad se redujo a O(n log n), con 100 eventos solo se requieren ~460 operaciones.

**Problema 2: Serialización cíclica en JSON**
- **Situación inicial**: Al serializar un Evento que contiene Recursos, y cada Recurso podría tener referencia a Eventos, se creaba un ciclo infinito.
- **Síntoma**: `json.dump()` fallaba con `RecursionError` o producía archivos enormes.
- **Solución implementada**: Se diseñó un sistema de serialización "unidireccional":
  1. Los Recursos se serializan completamente con todos sus atributos
  2. Los Eventos se serializan con solo los IDs de los Recursos (no los objetos completos)
  3. Al deserializar, primero se recrean todos los Recursos y se guardan en un diccionario por ID
  4. Luego se recrean los Eventos, buscando los Recursos por ID en el diccionario
- **Resultado**: Archivos JSON compactos (20KB para 50 eventos) sin problemas de recursión.

**Problema 3: Validación inconsistente de restricciones con múltiples unidades**
- **Situación inicial**: `RestriccionCapacidad` contaba simplemente cuántos recursos de un tipo había en un evento, pero si un recurso tenía capacidad=3 y se solicitaba 1 unidad, contaba como 1.
- **Síntoma**: Un evento podía solicitar 4 investigadores (cada uno capacidad=1) y 1 estación de trabajo (capacidad=4) contando como solo 1 recurso computacional, violando el espíritu de la restricción.
- **Solución implementada**: Se diferenciaron "recursos físicos" de "unidades solicitadas". Las restricciones ahora consideran:
  1. Para restricciones de co-requisito y exclusión: presencia/ausencia del recurso físico
  2. Para restricciones de capacidad: suma de las unidades solicitadas de cada recurso del tipo
- **Resultado**: Validación más precisa que refleja mejor la realidad del dominio.

**Problema 4: Estado inconsistente entre pestañas en Streamlit**
- **Situación inicial**: Cambios en una pestaña (ej: eliminar evento) no se reflejaban en otras pestañas sin recargar manualmente.
- **Síntoma**: Usuario eliminaba un evento en pestaña "Eventos" pero al ir a "Dashboard" todavía aparecía.
- **Solución implementada**: Se centralizó el estado en `st.session_state['planificador']` y se forzó rerun después de operaciones mutadoras usando `st.rerun()`.
- **Resultado**: Experiencia de usuario consistente con actualización en tiempo real.

## **4. Lógica del Sistema "Tras Bambalinas"**

### **4.1 Algoritmo de Planificación de Eventos (Paso a Paso)**

Cuando un usuario solicita planificar un nuevo evento, el sistema ejecuta una secuencia de validaciones cada vez más costosas computacionalmente:

```python
def planificar_evento(self, ...):
    # 1. Validaciones básicas (O(1))
    if inicio >= fin: return error
    if duracion > 7 días: return error
    
    # 2. Validación de recursos existentes (O(k) donde k = recursos solicitados)
    for recurso_id, cantidad in recursos_seleccionados:
        recurso = obtener_recurso(recurso_id)
        if not recurso: return error
        if cantidad > recurso.capacidad: return error
    
    # 3. Validación de restricciones estáticas (O(r) donde r = restricciones)
    es_valido, errores = validar_restricciones(recursos, evento_temp, restricciones)
    if not es_valido: return error
    
    # 4. Validación de conflictos temporales (O(n log n) donde n = eventos existentes)
    sin_conflictos, errores = verificar_conflictos(evento_temp)
    if not sin_conflictos:
        if buscar_hueco_automaticamente:
            # 5. Búsqueda de huecos (O(m * n log n) donde m = intentos)
            return buscar_hueco_automatico(...)
        else:
            return error
    
    # 6. Creación y almacenamiento del evento (O(1))
    evento = Evento(...)
    gestor_eventos.agregar_evento(evento)
    return éxito
```

**Innovación en el paso 4**: En lugar del enfoque naive de comparar intervalos por pares, el algoritmo transforma el problema a uno de "máima superposición en puntos". Para cada recurso:
- Se extraen todos los intervalos de eventos existentes que usan ese recurso y se solapan con el nuevo evento
- Se convierten a puntos (inicio: +cantidad, fin: -cantidad)
- Se ordenan y se barre acumulando, encontrando el máximo simultáneo
- Si el máximo + cantidad_solicitada > capacidad_recurso → conflicto

Este algoritmo es óptimo para el problema y se ejecuta en tiempo O(n log n) para cada recurso.

### **4.2 Sistema de Restricciones como Motor de Inferencia**

Las restricciones implementan un sistema de lógica proposicional básica:

**Co-requisitos**: Implementan implicación lógica (A → B)
- Si recurso_principal ∈ recursos_solicitados
- Entonces recurso_requerido ∈ recursos_solicitados
- Equivalente lógico: ¬(A ∧ ¬B)

**Exclusiones mutuas**: Implementan disyunción exclusiva (A ⊕ B)
- No (A ∈ recursos_solicitados ∧ B ∈ recursos_solicitados)
- Permite casos: ninguno, solo A, solo B
- Equivalente lógico: ¬(A ∧ B)

**Capacidades**: Implementan sumatorias con límites
- Σ(cantidad_solicitada(recurso) ∀ recurso ∈ tipo) ≤ límite
- Requiere mantener contadores por tipo de recurso

El sistema puede extenderse fácilmente con nuevos tipos de restricciones como:
- **RestriccionPrecedencia**: Evento A debe terminar antes que evento B empiece
- **RestriccionAgrupacion**: Si se usa recurso A, también deben usarse todos los recursos del conjunto {B, C, D}
- **RestriccionPresupuesto**: Costo total de recursos ≤ límite presupuestario

### **4.3 Persistencia como Sistema de Versionado Implícito**

El sistema de persistencia implementa características avanzadas:

**Migración automática**: Al cargar `datos.json` (formato antiguo), detecta la ausencia de campo `restricciones` y automáticamente:
1. Carga datos en formato antiguo
2. Aplica restricciones predeterminadas
3. Guarda en nuevo formato `datos_sistema.json`
4. Notifica al usuario de la migración

**Integridad referencial**: Durante la carga:
```python
def cargar_sistema(archivo):
    # Fase 1: Cargar todos los recursos
    recursos_por_id = {}
    for recurso_data in datos["recursos"]:
        recurso = Recurso.from_dict(recurso_data)
        recursos_por_id[recurso.id] = recurso
    
    # Fase 2: Cargar eventos con referencias a recursos
    for evento_data in datos["eventos"]:
        recursos_reconstruidos = []
        for recurso_ref in evento_data["recursos"]:
            if isinstance(recurso_ref, dict):
                recurso_id = recurso_ref["id"]
                if recurso_id in recursos_por_id:
                    recursos_reconstruidos.append(recursos_por_id[recurso_id])
                else:
                    raise ErrorIntegridad(f"Recurso {recurso_id} no existe")
        
        evento_data["recursos"] = recursos_reconstruidos
        evento = Evento.from_dict(evento_data)
        gestor_eventos.agregar_evento(evento)
    
    return gestor_eventos, gestor_recursos, restricciones
```

**Backup con metadatos**: Cada backup incluye metadatos de contexto:
- Fecha y hora exacta de creación
- Versión del esquema de datos
- Conteos de recursos y eventos
- Checksum para detección de corrupción

## **5. Lecciones Aprendidas y Conclusiones**

### **5.1 Lecciones Técnicas**

1. **Las operaciones con tiempo son más complejas de lo esperado**: Inicialmente se subestimó la complejidad de manejar zonas horarias, horarios de verano, y comparaciones de intervalos. La lección fue adoptar UTC como estándar interno desde el inicio y realizar conversiones solo en los límites del sistema.

2. **El diseño de interfaces afecta profundamente la extensibilidad**: La decisión temprana de definir protocolos (`IRecursoProtocol`, `IEventoProtocol`) permitió desarrollar módulos en paralelo y realizar pruebas unitarias aisladas. En contraste, el sistema de restricciones inicial (con validación acoplada a la lógica temporal) requirió refactorización significativa.

3. **La persistencia de objetos relacionados requiere estrategia**: El primer intento de usar `pickle` para serialización fue abandonado por problemas de portabilidad y versionado. JSON manual requirió más código pero resultó en un sistema más robusto y debuggable.

4. **Las interfaces de usuario consumen más tiempo del planeado**: El 40% del tiempo de desarrollo se dedicó a la interfaz Streamlit, particularmente a manejar estado entre interacciones y proporcionar feedback inmediato. La lección fue construir primero una API CLI funcional y luego añadir la interfaz gráfica.

### **5.2 Lecciones de Proceso**

1. **El diseño previo paga dividendos**: Las 2 semanas dedicadas a modelado de dominio y diseño de algoritmos evitaron al menos 3 refactorizaciones mayores durante la implementación. Los diagramas de secuencia iniciales, aunque incompletos, sirvieron como "mapa" durante el desarrollo.

2. **Las pruebas deberían escribirse junto con el código**: Inicialmente se pospuso la escritura de tests, lo que resultó en dificultad para depurar el sistema de restricciones. Cuando se adoptó TDD para el módulo de persistencia, la calidad del código mejoró notablemente.

3. **La documentación viva es esencial**: Mantener el README.md actualizado en cada hito mayor evitó la "amnesia de proyecto" y facilitó la reintegración después de interrupciones.

### **5.3 Conclusiones**

El proyecto resultó en un sistema robusto que no solo cumple con los requisitos básicos sino que implementa funcionalidades avanzadas propias de sistemas profesionales. La arquitectura por capas demostró ser efectiva para manejar la complejidad, permitiendo que cada módulo evolucionara independientemente.

Las decisiones más acertadas fueron:
1. Modelar recursos con capacidad en lugar de instancias individuales
2. Separar completamente la validación de restricciones de la verificación temporal
3. Implementar un algoritmo de barrido de línea para detección de conflictos
4. Diseñar un sistema de persistencia con migración automática

Si se empezara de nuevo, se enfatizaría aún más la separación entre lógica de negocio e infraestructura, posiblemente utilizando inyección de dependencias para hacer los componentes aún más testables. También se exploraría el uso de una base de datos temporal especializada para consultas de intervalos más complejas.

El sistema está preparado para extensiones futuras como:
- Planificación de eventos recurrentes
- Optimización multi-objetivo (minimizar coste, maximizar utilización)
- Integración con sistemas de calendario externos (Google Calendar, Outlook)
- Análisis predictivo de demanda de recursos

En conclusión, el proyecto demuestra que con un diseño cuidadoso y atención a los principios de arquitectura de software, es posible construir sistemas complejos que sean a la vez robustos y mantenibles.

from datetime import datetime 
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import uuid 

@dataclass
class Recurso:
    """Clase que representa un recurso en el centro de investigación"""
    id: str = ""
    nombre: str = ""
    tipo: str = "" #computacional, humano, espacio, equipo
    capacidad: int = 1 #Para recursos que posean múltiples unidades
    atributos: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self): # Función que es un método de instancia, opera sobre instancias
        """Validaciones después de la inicialización"""
        if not self.id:
            self.id = f"recurso_{uuid.uuid4().hex[:8]}"
        
        if not self.nombre:        # Validar que nombre no esté vacío
            raise ValueError("El nombre del recurso es obligatorio")
        
        if not self.tipo:          # Validar que tipo no esté vacío
            raise ValueError("El tipo del recurso es obligatorio")
        
        if self.capacidad < 1:
            raise ValueError("La capacidad debe de ser al menos uno")

    @classmethod #decorador que se utiliza para operar en la clase
    def from_dict(cls, data: Dict[str, Any]) -> "Recurso":
        """Crea una instancia de Recurso desde diccionario"""
        return cls( 
            id=data.get('id', ''),
            nombre=data.get('nombre', ''),
            tipo=data.get('tipo', ''),
            capacidad=data.get('capacidad', 1),
            atributos=data.get('atributos', {}),
        )
    def to_dict(self) ->Dict[str, Any]:
        """Convierte el recurso a diccionario para serialización"""
        #Serialización :Guardar los objetos para ser utilizados después
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'capacidad': self.capacidad,
            'atributos': self.atributos,
        } 
    
    def es_compatible_con(self, other: 'Recurso') ->bool:
        """Verifica si este recurso es compatible con otro para restricciones"""
        #Lógica básica de compatibilidad(puede extenderse)
        if self.tipo == "computacional" and other.tipo == "humano":
            return True
        return False  
    
    def __hash__(self):
        """Permite utilizar Recurso en conjuntos y como clave de diccionarios"""
        return hash(self.id)
    
    def __eq__(self, other) ->bool:
        """Compara recursos por ID"""
        if not isinstance(other, Recurso):
            return False
        return self.id == other.id
    
    def __str__(self):
        """Representación legible del Recurso"""
        capacidad_str = f" (x{self.capacidad})" if self.capacidad > 1 else ""  
        return f"{self.nombre}{capacidad_str} [{self.tipo}]"  
    
    def __repr__(self):
        """Se utiliza para debugging"""
        return f"Recurso(id='{self.id}', nombre='{self.nombre}', tipo='{self.tipo}')"

class GestorRecursos:
    """Clase para gestionar diversos recursos"""
    def __init__(self):
        self.recursos : Dict[str, Recurso] = {}

    def agregar_recurso(self, recurso: Recurso) ->bool:
        """Agrega un recurso al gestor"""
        if recurso.id in self.recursos:
            return False
        self.recursos[recurso.id] = recurso
        return True
    
    def obtener_recurso(self, id_recurso:str) ->Optional[Recurso]:#Puede devolver None
        """Obtiene un recurso por ID""" 
        return self.recursos.get(id_recurso)
    
    def obtener_por_tipo(self, tipo:str) ->List[Recurso]:
        """Devuelve una lista con los recursos del mismo tipo"""
        return[ r for r in self.recursos.values() if r.tipo == tipo]
    
    def buscar_por_nombre(self, nombre:str) ->List[Recurso]:
        """Obtiene los recursos por nombre(Búsqueda parcial)"""
        nombre_lower = nombre.lower()
        return [ r for r in self.recursos.values() if nombre_lower in r.nombre.lower()]
    
    def eliminar_recurso(self, id_recurso:str) ->bool:
        """Elimina un recurso del gestor"""
        if id_recurso in self.recursos:
            del self.recursos[id_recurso]
            return True
        return False
    
    def cargar_desde_lista(self, lista_recursos:List[Dict[str, Any]]):
        """Carga recursos de una lista de diccionarios"""
        for recurso_data in lista_recursos:
            recurso = Recurso.from_dict(recurso_data)
            self.agregar_recurso(recurso)

    def to_list(self) ->List[Dict[str, Any]]:
        """Convierte los recursos en diccionarios que se almacenan en lista"""
        return[recurso.to_dict() for recurso in self.recursos.values()]

    def __len__(self):
        """Cantidad de recursos gestionados"""
        return len(self.recursos)
    
    def __iter__(self):
        """Permite iterar sobre los recursos"""
        return iter(self.recursos.values())
    
#Recursos predefinidos para el centro de IA
def crear_recursos_predeterminados() -> GestorRecursos:
    """Crea los recursos predeterminados de un centro de investigación de IA"""
    gestor = GestorRecursos()  
    recursos_base = [
        # Recursos computacionales
        Recurso("cluster_gpu_a100", "Cluster GPU A100 (8x NVIDIA A100)", "computacional", 1, {
            "memoria_gpu": "320GB",
            "procesadores": "2x AMD EPYC",
            "ram": "512GB",
            "almacenamiento": "50TB NVMe",
            "consumo_energia": "6.5kW"
        }),
        
        Recurso("cluster_gpu_v100", "Cluster GPU V100 (4x NVIDIA V100)", "computacional", 1, {
            "memoria_gpu": "128GB", 
            "procesadores": "2x Intel Xeon",
            "ram": "256GB",
            "almacenamiento": "20TB SSD",
            "consumo_energia": "3.2kW"
        }),
        
        Recurso("servidor_cpu", "Servidor CPU High-Memory", "computacional", 2, {
            "procesadores": "2x AMD EPYC 7742",
            "ram": "1TB",
            "almacenamiento": "100TB HDD",
            "nucleos": "128"
        }),
        
        Recurso("estacion_trabajo", "Estación de Trabajo RTX 4090", "computacional", 4, {
            "gpu": "NVIDIA RTX 4090",
            "ram": "64GB",
            "almacenamiento": "4TB NVMe"
        }),
        
        Recurso("servidor_externo", "Servidor Cloud Externo (AWS/GCP)", "computacional", 2, {
            "proveedor": "AWS EC2 P4d",
            "gpu": "8x NVIDIA A100",
            "ram": "1152GB",
            "ubicacion": "us-east-1",
            "acceso": "VPN exclusiva"
        }),

        Recurso("robot_aprendizaje", "Robot de Aprendizaje por Refuerzo", "equipo", 1, {
            "tipo": "Manipulador 6DOF",
            "sensores": ["RGB-D", "LiDAR", "Táctiles"],
            "controlador": "NVIDIA Jetson AGX",
            "software": "ROS2, PyTorch",
            "area_requerida": "16m²"
        }),
        
        # Recursos humanos
        Recurso("investigador_vision", "Investigador Senior - Visión Computacional", "humano", 1, {
            "especialidad": "Computer Vision",
            "experiencia": "5+ años",
            "certificaciones": ["PyTorch", "OpenCV", "TensorFlow"]
        }),
        
        Recurso("investigador_nlp", "Investigador Senior - NLP", "humano", 1, {
            "especialidad": "Natural Language Processing",
            "experiencia": "4+ años", 
            "certificaciones": ["Transformers", "HuggingFace", "spaCy"]
        }),
        
        Recurso("ingeniero_mlops", "Ingeniero de MLOps", "humano", 2, {
            "especialidad": "MLOps & DevOps",
            "experiencia": "3+ años",
            "certificaciones": ["Docker", "Kubernetes", "AWS", "MLflow"]
        }),
        
        Recurso("cientifico_datos", "Científico de Datos", "humano", 3, {
            "especialidad": "Data Science",
            "experiencia": "2+ años",
            "certificaciones": ["Python", "Pandas", "Scikit-learn"]
        }),
        
        # Espacios
        Recurso("lab_datos_sensibles", "Laboratorio de Datos Sensibles", "espacio", 1, {
            "capacidad_personas": 4,
            "seguridad": "Nivel 3",
            "equipamiento": ["Estaciones seguras", "Almacenamiento encriptado"]
        }),
        
        Recurso("sala_servidores", "Sala de Servidores", "espacio", 1, {
            "capacidad_personas": 2,
            "temperatura_controlada": True,
            "ups": "Doble conversión"
        }),
        
        Recurso("sala_reuniones", "Sala de Reuniones Principal", "espacio", 1, {
            "capacidad_personas": 12,
            "equipamiento": ["Proyector 4K", "Sistema de video conferencia"]
        }),
        
        Recurso("lab_prototipado", "Laboratorio de Prototipado", "espacio", 1, {
            "capacidad_personas": 6,
            "equipamiento": ["Impresoras 3D", "Sensores IoT", "Kits de desarrollo"]
        })
    ]

    for recurso in recursos_base:
        gestor.agregar_recurso(recurso)

    return gestor
           


    

    
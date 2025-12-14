from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional 
import uuid
from dataclasses import dataclass, field
from resources1 import Recurso

@dataclass
class Evento:
    """clase que representa a un evento en el sistema de planificación"""
    nombre: str
    inicio: datetime
    fin: datetime 
    recursos: List[Recurso]
    tipo: str # entrenamiento, procesamiento, investigación, reunión, seminario, inferencia
    id: str field(default_factory = lambda: f"evento_{uuid.uuid4().hex[:8]}")
    descripción: str = ""
    estado: str #planificado, en curso, completado, cancelado 
    prioridad: int=1 #1-5, donde el número 5 es el máximo de prioridad
    metadata: Dict[str, Any] = field(default_factory=dict)

def __post_init__(self):
    """Validaciones después de la inicialización"""
    self.validar_fechas()
    self.validar_recursos()
    self.validar_tipo()

def validar_fechas(self):
    """si las fechas son consistentes, valida"""
    if self.inicio >= self.fin:
        raise ValueError ("El inicio debe ser anterior al fin")
    
    if self.fin - self.inicio > timedelta(days=7):
        raise ValueError ("Los eventos no pueden durar más de 7 días")
    
def validar_recurso(self):
    """Verifica si los recursos son válidos"""
    if not self.recursos:
        raise ValueError ("El evento debe poseer al menos un recurso")
    
    #Para comprobar que todos los recursos son instancias de la clase Recurso
    for recurso in self.recursos:
    if not isinstance(recurso, Recurso):
        raise TypeError("Todos los recursos deben ser instancias de la clase Recurso")

def validar_tipo(self):
    """Valida el tipo de evento"""
    tipos_válidos= ["entrenamiento", "procesamiento", "investigación", "reunión", "seminario", "inferencia"]
    if self.tipo not in tipos_válidos:
        raise ValueError (f"Tipo de evento inválido.Debe ser uno de {','.join(tipos_válidos)}")
    

                          
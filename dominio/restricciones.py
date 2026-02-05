"""
Sistema de restricciones para el planificador de eventos
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

# IMPORTANTE: Evita dependencias circulares
if TYPE_CHECKING:
    # Solo para type checking durante desarrollo
    from ..dominio.recursos import Recurso
    from ..dominio.eventos import Evento
    from ..core.interfaces import IRecursoProtocol, IEventoProtocol

class Restriccion(ABC):
    """Clase abstracta que sirve de plantilla para las demás clases"""
    # Todas las subclases deberán implementar los métodos abstractos de la clase abstracta
    @abstractmethod
    def es_valida(self, recursos: List['Recurso'], evento: 'Evento') ->bool:
        """Valida si la combinación de recursos cumple con la restricción"""
        pass 

    @abstractmethod
    def mensaje_error(self)->str:
        """Devuelve el mensaje de error si la restricción no se cumple"""
        pass

class RestriccionCoRequisito(Restriccion):
    """
    Al utilizar el recurso A es estrictamente necesario utilizar el recurso B
    Ejemplo: Cluster GPU depende de Investigador especializado
    """
    def __init__(self,id_recurso_principal: str, id_recurso_requerido:str):
            if id_recurso_principal == id_recurso_requerido:
                raise ValueError( f"Un recurso no puede ser co-requisito de sí mismo")
            self.principal = id_recurso_principal
            self.requerido = id_recurso_requerido
                
    
    def es_valida(self,recursos: List['Recurso'], evento:'Evento')->bool:
        # Para saber si posee la lista de recursos, el recurso principal y requerido
        tiene_principal = any(r.id == self.principal for r in recursos)
        # La función any() devuelve True si se cumple al menos para uno y False si no se cumpla para ninguno
        tiene_requerido = any(r.id == self.requerido for r in recursos)

        if tiene_principal and not tiene_requerido:
            return False
        return True
        
    def mensaje_error(self) ->str:
        return (f"Para la utilización del recurso: {self.principal}, "
                f"es necesario emplear también el recurso: {self.requerido}")
     
class RestriccionExclusionMutua(Restriccion):
    """Si el recurso A es utilizado entonces el recurso B no debe utilizarse
    Ejemplo: lab de datos sensibles no debe usarse con servidores externos
    """
    
    def __init__(self, id_recurso_a: str, id_recurso_b: str):
        if id_recurso_a == id_recurso_b:
            raise ValueError(f"Un recurso no puede excluirse a sí mismo")
        self.recurso_a = id_recurso_a
        self.recurso_b = id_recurso_b
        
    def es_valida(self, recursos:List['Recurso'], evento:'Evento') ->bool:
        tiene_recurso_a = any(r.id == self.recurso_a for r in recursos)
        tiene_recurso_b = any(r.id == self.recurso_b for r in recursos)

        return not (tiene_recurso_a and tiene_recurso_b)
    
    def mensaje_error(self) ->str:
        return f"El recurso {self.recurso_a} y {self.recurso_b} no se pueden utilizar juntos"
    
class RestriccionCapacidad(Restriccion):
    """Limita la cantidad de recursos que se pueden utilizar para un evento de un tipo específico
    Ejemplo: Máximo dos investigadores por evento, dos recursos de tipo computacional, etc 
    """
    def __init__(self, capacidad_maxima: int, tipo_recurso: str):
        if capacidad_maxima <= 0:
            raise ValueError("La capacidad máxima debe ser mayor a 0")
    
        self.capacidad_maxima = capacidad_maxima
        self.tipo_recurso = tipo_recurso

    def es_valida(self, recursos:List['Recurso'], evento:'Evento') ->bool:
        # Vamos a contar la cantidad de recursos que sean del tipo especificado
        cantidad = sum( 1 for r in recursos if r.tipo == self.tipo_recurso)

        # Comprobamos si esta cantidad no se excede a la máxima disponibilidad
        return cantidad <= self.capacidad_maxima
    
    def mensaje_error(self) ->str:
        return f"Máximo {self.capacidad_maxima} recursos de tipo '{self.tipo_recurso}' permitidos por evento"
    
def crear_restricciones_predeterminadas() -> List[Restriccion]:
    """
    Crea las restricciones predeterminadas para un centro de investigación de IA
    
    Returns:
        Lista de restricciones configuradas para el dominio específico
    """
    restricciones = [
        #  CO-REQUISITOS 
        # Un cluster GPU avanzado requiere un investigador especializado
        RestriccionCoRequisito(
            id_recurso_principal="cluster_gpu_a100",
            id_recurso_requerido="investigador_vision"
        ),
        
        # El laboratorio de datos sensibles requiere un científico de datos
        RestriccionCoRequisito(
            id_recurso_principal="lab_datos_sensibles",
            id_recurso_requerido="cientifico_datos"
        ),
        
        # La sala de servidores requiere un ingeniero de MLOps
        RestriccionCoRequisito(
            id_recurso_principal="sala_servidores",
            id_recurso_requerido="ingeniero_mlops"
        ),
        
        #          EXCLUSIONES MUTUAS 
        # NO USAR JUNTOS: Laboratorio de datos sensibles con servidores externos
        # (Por razones de seguridad y cumplimiento normativo)
        RestriccionExclusionMutua(
            id_recurso_a="lab_datos_sensibles",
            id_recurso_b="servidor_externo"
        ),
        
        # NO USAR JUNTOS: Dos clusters GPU grandes
        # (Por limitaciones de consumo energético y refrigeración)
        RestriccionExclusionMutua(
            id_recurso_a="cluster_gpu_a100",
            id_recurso_b="cluster_gpu_v100"
        ),
        
        # NO USAR JUNTOS: Sala de servidores y laboratorio de prototipado
        # (Por interferencia electromagnética con equipos sensibles)
        RestriccionExclusionMutua(
            id_recurso_a="sala_servidores",
            id_recurso_b="lab_prototipado"
        ),
        
        # NO USAR JUNTOS: Robot de aprendizaje con sala de reuniones principal
        # (Por requisitos de espacio y seguridad física)
        RestriccionExclusionMutua(
            id_recurso_a="robot_aprendizaje",
            id_recurso_b="sala_reuniones"
        ),
        
        # RESTRICCIONES DE CAPACIDAD 
        # Máximo 4 recursos humanos por evento (para mantener grupos manejables)
        RestriccionCapacidad(
            tipo_recurso="humano",
            capacidad_maxima=4
        ),
        
        # Máximo 2 recursos computacionales por evento (limitación de energía)
        RestriccionCapacidad(
            tipo_recurso="computacional",
            capacidad_maxima=2
        ),
        
        # Máximo 1 espacio por evento (no se pueden usar múltiples espacios simultáneamente)
        RestriccionCapacidad(
            tipo_recurso="espacio",
            capacidad_maxima=1
        )
    ]
    return restricciones

def validar_restricciones(recursos: List['Recurso'], evento: 'Evento', restricciones:List['Restriccion']) ->tuple:
    """Valida todas las restricciones para un evento"""
    errores = []
    
    for restriccion in restricciones:
        if not restriccion.es_valida(recursos, evento):
            errores.append(restriccion.mensaje_error())

    return len(errores) == 0, errores

def obtener_restricciones_por_tipo(restricciones: List[Restriccion], tipo_restriccion: type) ->List[Restriccion]:
    """Permite obtener las restricciones de un tipo específico"""
    return [r for r in restricciones if isinstance(r, tipo_restriccion)]
    






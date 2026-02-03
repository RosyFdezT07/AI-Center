"""
Planificador Inteligente de Eventos - Centro de Investigación en IA
Paquete principal para gestión de eventos con recursos limitados.
"""

__version__ = "1.0.0"
__author__ = "Equipo de Desarrollo"

# Re-exportaciones principales para facilitar el acceso
from .dominio.recursos import Recurso, GestorRecursos
from .dominio.eventos import Evento, GestorEventos
from .dominio.restricciones import (
    Restriccion, 
    RestriccionCoRequisito, 
    RestriccionExclusionMutua, 
    RestriccionCapacidad
)
from .aplicacion.planificador import Planificador
from .infraestructura.persistencia import Persistencia

# Funciones de fábrica
from .dominio.recursos import crear_recursos_predeterminados
from .dominio.restricciones import crear_restricciones_predeterminadas

__all__ = [
    # Modelos
    'Recurso',
    'Evento',
    
    # Gestores
    'GestorRecursos',
    'GestorEventos',
    
    # Restricciones
    'Restriccion',
    'RestriccionCoRequisito',
    'RestriccionExclusionMutua', 
    'RestriccionCapacidad',
    
    # Lógica principal
    'Planificador',
    
    # Persistencia
    'Persistencia',
    
    # Funciones de fábrica
    'crear_recursos_predeterminados',
    'crear_restricciones_predeterminadas',
]
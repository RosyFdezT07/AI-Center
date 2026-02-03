"""
Módulo dominio - Entidades y reglas de negocio
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Importaciones solo para type checking
    from datetime import datetime
    from typing import List

# Exportar desde recursos.py
from .recursos import Recurso, GestorRecursos, crear_recursos_predeterminados

# Exportar desde eventos.py  
from .eventos import Evento, GestorEventos, crear_evento_ejemplo

# Exportar desde restricciones.py
from .restricciones import (
    Restriccion,
    RestriccionCoRequisito,
    RestriccionExclusionMutua,
    RestriccionCapacidad,
    crear_restricciones_predeterminadas,
    validar_restricciones,
    obtener_restricciones_por_tipo
)

__all__ = [
    # Recursos
    'Recurso',
    'GestorRecursos',
    'crear_recursos_predeterminados',
    
    # Eventos
    'Evento',
    'GestorEventos',
    'crear_evento_ejemplo',
    
    # Restricciones
    'Restriccion',
    'RestriccionCoRequisito',
    'RestriccionExclusionMutua',
    'RestriccionCapacidad',
    'crear_restricciones_predeterminadas',
    'validar_restricciones',
    'obtener_restricciones_por_tipo'
]
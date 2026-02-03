"""
Definiciones de tipos para el sistema
"""
from typing import Dict, Any, Union, List, TypedDict

# Tipos para serialización
RecursoDict = Dict[str, Any]
EventoDict = Dict[str, Any]
RecursoId = str

# Tipos para restricciones
RestriccionDict = Dict[str, Any]

__all__ = ['RecursoDict', 'EventoDict', 'RecursoId', 'RestriccionDict']
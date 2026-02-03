"""
Módulo core - Definiciones de tipos e interfaces base
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Solo para type checking, evita dependencias circulares
    from datetime import datetime
    from typing import Any, Dict, List

# Re-exportar desde interfaces.py y tipos.py
from .interfaces import IRecursoProtocol, IEventoProtocol
from .tipos import RecursoDict, EventoDict, RecursoId

__all__ = [
    'IRecursoProtocol',
    'IEventoProtocol',
    'RecursoDict',
    'EventoDict',
    'RecursoId'
]
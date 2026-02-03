"""
Protocolos para evitar dependencias circulares
"""
from typing import Protocol, runtime_checkable
from datetime import datetime

@runtime_checkable
class IRecursoProtocol(Protocol):
    """Protocolo para recursos sin dependencias circulares"""
    id: str
    nombre: str
    tipo: str
    capacidad: int
    
    def to_dict(self) -> dict: ...
    def es_compatible_con(self, other) -> bool: ...

@runtime_checkable  
class IEventoProtocol(Protocol):
    """Protocolo para eventos sin dependencias circulares"""
    id: str
    nombre: str
    inicio: datetime
    fin: datetime
    tipo: str
    
    def se_solapa_con(self, otro_evento) -> bool: ...
    def contiene_recurso(self, recurso) -> bool: ...
    def to_dict(self) -> dict: ...
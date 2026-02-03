"""
Gestión de eventos
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional 
import uuid
from dataclasses import dataclass, field

# Importación relativa - sin dependencia circular
from .recursos import Recurso 

@dataclass
class Evento:
    """clase que representa a un evento en el sistema de planificación"""
    nombre: str
    inicio: datetime
    fin: datetime 
    recursos: List[Recurso]
    tipo: str # entrenamiento, procesamiento, investigación, reunión, seminario, inferencia
    id: str = field(default_factory=lambda: f"evento_{uuid.uuid4().hex[:8]}")
    descripcion: str = ""
    prioridad: int = 1  # 1-5, donde el número 5 es el máximo de prioridad
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validaciones después de la inicialización"""
        self.validar_fechas()
        self.validar_recursos()
        self.validar_tipo()

    def validar_fechas(self):
        """si las fechas son consistentes, valida"""
        if self.inicio >= self.fin:
            raise ValueError("El inicio debe ser anterior al fin")
    
        if self.fin - self.inicio > timedelta(days=7):
            raise ValueError("Los eventos no pueden durar más de 7 días")
        
        
    def validar_recursos(self):
        """Verifica si los recursos son válidos"""
        if not self.recursos:
            raise ValueError("El evento debe poseer al menos un recurso")
    
    # Para comprobar que todos los recursos son instancias de la clase Recurso
        for recurso in self.recursos:
            if not isinstance(recurso, Recurso):
                raise TypeError("Todos los recursos deben ser instancias de la clase Recurso")

    def validar_tipo(self):
        """Valida el tipo de evento"""
        tipos_validos = ["entrenamiento", "procesamiento", "investigación", "reunión", "seminario", "inferencia"]
        if self.tipo not in tipos_validos:
            raise ValueError(f"Tipo de evento inválido.Debe ser uno de: {','.join(tipos_validos)}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Evento':
        """Deserialización, a partir de un diccionario"""
        # Conversión de fecha
        inicio = datetime.fromisoformat(data['inicio']) if isinstance(data['inicio'], str) else data['inicio']
        fin = datetime.fromisoformat(data['fin']) if isinstance(data['fin'], str) else data['fin']

        # Los recursos pueden ser diccionarios o objetos Recurso
        recursos_data = data.get('recursos', [])
        recursos = []
        
        for recurso_data in recursos_data:
            if isinstance(recurso_data, dict):
                # Convertir diccionario a objeto Recurso
                recurso = Recurso.from_dict(recurso_data)
                recursos.append(recurso)
            else:
                # Ya es un objeto Recurso
                recursos.append(recurso_data)

        evento = cls(
            id=data.get('id', ''),
            nombre=data['nombre'],
            inicio=inicio,
            fin=fin,
            recursos=recursos,
            tipo=data['tipo'],
            descripcion=data.get('descripcion', ''),
            prioridad=data.get('prioridad', 1),
            metadata=data.get('metadata', {})
        )
        
        estado_guardado = data.get('estado')
        if estado_guardado == 'cancelado':
            evento.metadata["cancelado"] = True
    
        return evento

    def to_dict(self) ->Dict[str, Any]:
        """Para la serialización de eventos a diccionarios"""
        return {
            'id':self.id,
            'nombre':self.nombre,
            'inicio':self.inicio.isoformat(),
            'fin':self.fin.isoformat(),
            'recursos':[recurso.to_dict() for recurso in self.recursos],
            'tipo':self.tipo,
            'descripcion':self.descripcion,
            'estado':self.estado,
            'prioridad':self.prioridad,
            'metadata':self.metadata
        }           

    @property
    def duracion(self) ->timedelta:
        """Permite calcular la duración del evento"""
        return self.fin - self.inicio
    
    @property
    def duracion_horas(self) -> float:
        """Permite calcular la duración del evento en horas"""
        return self.duracion.total_seconds() / 3600
    
    @property
    def estado(self) -> str:
        ahora = datetime.now()
        
        # Buscamos la llave 'cancelado' y 
        # nos aseguramos de que sea True (si no existe, devuelve False por defecto)
        
        if self.metadata.get("cancelado") is True:
            return "cancelado"
            
        if ahora < self.inicio:
            return "planificado"
        elif self.inicio <= ahora <= self.fin:
            return "en_curso"
        else:
            return "completado"
    
    def cancelar(self):
        """Marca el evento como cancelado de forma irreversible"""
        self.metadata["cancelado"] = True
        self.metadata["fecha_cancelacion"] = datetime.now().isoformat()
    
    def se_solapa_con(self, otro_evento: 'Evento', margen: Optional[timedelta] = None) ->bool:
        """Verifica si un evento se solapa con otro"""
        if margen is None:
            margen = timedelta(minutes = 15) # Margen por defecto de 15 minutos

        inicio_self = self.inicio - margen
        fin_self = self.fin + margen 
        inicio_otro = otro_evento.inicio 
        fin_otro = otro_evento.fin

        return (inicio_self < fin_otro) and (inicio_otro < fin_self)

    def tiene_recursos_comunes(self, otro_evento: 'Evento') -> List[Recurso]: 
        comunes = []
        ids_propios = {r.id for r in self.recursos}
        for recurso in otro_evento.recursos:
            if recurso.id in ids_propios:
                comunes.append(recurso)
        return comunes
    
    def contiene_recurso(self, recurso: Recurso) ->bool:
        """Verifica si el evento posee un recurso en específico"""
        return recurso in self.recursos 

    def obtener_recursos_por_tipo(self, tipo:str) ->List[Recurso]:
        """Devuelve una lista con todos los recursos del mismo tipo que pertenezcan al evento"""
        return [r for r in self.recursos if r.tipo == tipo]

    def esta_activo_en(self, momento: datetime) ->bool:
        """Verifica si el evento se encuentra activo en un momento en específico"""
        return self.inicio <= momento <= self.fin
    
    def agregar_recurso(self, recurso: Recurso):
        """Agrega un recurso al evento""" 
        if not isinstance(recurso, Recurso):
            raise TypeError("El recurso debe ser una instancia de la clase Recurso") 

        if recurso not in self.recursos:
            self.recursos.append(recurso)

    def eliminar_recurso(self, recurso: Recurso):
        """Elimina un recurso del evento"""
        if recurso in self.recursos:
            self.recursos.remove(recurso)

    def __str__(self):
        """Representación legible del evento"""
        #Formatear recursos
        if not self.recursos: 
            recursos_str = "No hay recursos" 
        else:
            recursos_str = ", ".join([r.nombre for r in self.recursos[:2]])
            if len(self.recursos) > 2:
                recursos_str += f"y {len(self.recursos) - 2} más" 

        estado_iconos ={
            'planificado':"🗓️",
            'en_curso':"🟢",
            'completado':"✅",
            'cancelado':"❌"
        } 
        icono = estado_iconos.get(self.estado, "🗓️") 

        #Variables condicionales
        formato_completo = '%d/%m/%Y %H:%M'
        es_mismo_día = self.inicio.date() == self.fin.date()
        duracion_horas = (self.fin - self.inicio).total_seconds() / 3600

        #Lógica de formato condicional 
        if es_mismo_día:
            #Si la duración es menos de 12 horas
            if duracion_horas < 12:
                fecha_str = f"{self.inicio.strftime(formato_completo)}-{self.fin.strftime('%H:%M')}"
            else:
                #Si la duración de los días es mayor que 12 horas, día largo
                fecha_str = f"{self.inicio.strftime(formato_completo)}-{self.fin.strftime('%H:%M')}({int(duracion_horas)}h)"
        else:
            #Evento que cruza días
            fecha_str = f"{self.inicio.strftime(formato_completo)}-{self.fin.strftime(formato_completo)}"

        return f"{icono} {self.nombre} ({fecha_str}) - {recursos_str}"
    
    def __repr__(self):
        """Representación para debugging"""
        return (f"Evento(id='{self.id}', nombre='{self.nombre}', "
                f"inicio={self.inicio}, tipo= '{self.tipo}')")
    
class GestorEventos:
    """Clase para gestionar múltiples eventos"""
    def __init__(self):
        self.eventos: Dict[str, Evento] = {}

    def agregar_evento(self, evento: Evento) ->bool:
        """Agrega un evento al gestor de eventos"""
        if evento.id in self.eventos:
            return False
        self.eventos[evento.id] = evento
        return True
    
    def obtener_evento(self, id_evento:str) ->Optional[Evento]:
        """Obtiene un evento por id"""
        return self.eventos.get(id_evento)
    
    def obtener_fecha_inicio(self, fecha:datetime) ->List[Evento]:
        """Obtener todos los eventos que empiezan en una fecha específica( el mismo día)"""
        return [e for e in self.eventos.values() 
                if e.inicio.date()==fecha.date()]
    
    def obtener_por_rango_fecha(self, inicio:datetime, fin:datetime) ->List[Evento]:
        """Obtiene todos los eventos que ocurren en un rango de fechas"""
        return [e for e in self.eventos.values()
                if inicio <= e.inicio <= fin or inicio <= e.fin <= fin]
    
    def obtener_por_tipo(self, tipo:str) ->List[Evento]:
        """Obtiene todos los eventos que tengan un tipo específico"""
        return [e for e in self.eventos.values()
                if e.tipo == tipo]
    
    def obtener_por_recurso(self, recurso:Recurso) ->List[Evento]:
        """Obtiene todos los eventos que posean un recurso específico"""
        return [e for e in self.eventos.values()
                if e.contiene_recurso(recurso)]
    
    def eliminar_evento(self, id_evento: str) ->bool:
        """Elimina el evento que se desee de la clase GestorEvento"""
        if id_evento in self.eventos:
            del self.eventos[id_evento]
            return True
        return False
    
    def eventos_solapados(self, evento: Evento) ->List[Evento]:
        """Permite determinar todos los eventos que se solapan con el evento dado"""
        return [e for e in self.eventos.values() 
                if e.id != evento.id and e.se_solapa_con(evento)]
    
    def cargar_desde_lista(self, lista_eventos :List[Dict[str, Any]]):
        """Permite obtener el evento a partir de lista de diccionarios y agregarlo al gestor"""
        for evento_data in lista_eventos:
            evento = Evento.from_dict(evento_data)
            self.agregar_evento(evento)
            
    def cargar_desde_lista_con_recurso(self, lista_eventos: List[Dict[str, Any]], recursos_dict: Dict[str, Recurso]):
        """
        Carga eventos de una lista de diccionarios, reconstruyendo referencias a objetos Recurso
        a partir de un diccionario de recursos
        """
        
        for evento_data in lista_eventos:
            # Saltar si no hay recursos definidos 
            if 'recursos' not in evento_data:
                continue
            
            recursos_reconstruidos = []
            # Caso 1: Ya es un objeto Recurso: No debería pasar en JSON
            for recurso_item in evento_data['recursos']:
                if isinstance(recurso_item, Recurso):
                    recursos_reconstruidos.append(recurso_item)
                    continue
                
                if isinstance(recurso_item, dict):
                    recurso_id = recurso_item.get('id')
                    
                elif isinstance(recurso_item, str):
                    recurso_id = recurso_item
                    
                else:
                    # Formato no reconocido
                    continue
                
                #Buscar el recurso en el diccionario
                if recurso_id and recurso_id in recursos_dict:
                    recurso_obj = recursos_dict[recurso_id]
                    recursos_reconstruidos.append(recurso_obj)
                    
                elif recurso_id:
                    # Lanzar una advertencia
                    print (f"Recurso no encontrado: {recurso_id}")
                    
            # Actualizar el evento con los recursos reconstruidos 
            evento_data_actualizado = evento_data.copy()
            evento_data_actualizado['recursos'] = recursos_reconstruidos
                
            #Crear evento
            try: 
                evento = Evento.from_dict(evento_data_actualizado)
                self.agregar_evento(evento)
                        
            except Exception as e:
                print (f"Error al cargar evento {e}")
                        
                
    def to_list(self) ->List[Dict[str, Any]]:
        """Convierte todos los eventos a lista de diccionarios"""
        return [ evento.to_dict() for evento in self.eventos.values()]
    
    def __len__(self):
        """Permite saber la cantidad de eventos gestionados"""
        return len(self.eventos)
    
    def __iter__(self):
        """Permite iterar sobre todos los eventos"""
        return iter(self.eventos.values())

# Funciones de utilidad para eventos
def crear_evento_ejemplo() -> Evento:
    
    """Crea un evento de ejemplo para testing"""
    from datetime import datetime, timedelta
    
    # Crear algunos recursos de ejemplo
    cluster_gpu = Recurso("cluster_gpu_a100", "Cluster GPU A100", "computacional")
    investigador = Recurso("investigador_vision", "Investigador Visión", "humano")
    
    inicio = datetime.now() + timedelta(hours=1)
    fin = inicio + timedelta(hours=3)
    
    return Evento(
        nombre="Entrenamiento Modelo Vision",
        inicio=inicio,
        fin=fin,
        recursos=[cluster_gpu, investigador],
        tipo="entrenamiento",
        descripcion="Entrenamiento de red neuronal para clasificación de imágenes",
        prioridad=3
    )
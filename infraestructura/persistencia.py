# Módulo de Persistencia:

"""Encargado de cargar y guardar el estado del sistema"""

import json
from datetime import datetime
from typing import List, Any, Dict
import os

# Usando importaciones relativas 
from dominio.recursos import Recurso, GestorRecursos 
from dominio.eventos import Evento, GestorEventos
from dominio.restricciones import (
    Restriccion, RestriccionExclusionMutua, 
    RestriccionCoRequisito, RestriccionCapacidad,
    crear_restricciones_predeterminadas
)


class Persistencia:
    """Responsable de cargar y guardar los datos del sistema"""
     
    @staticmethod #La siguiente función no recibe parámetro(clase, instancia)
    def guardar_sistema( gestor_eventos: GestorEventos, gestor_recursos: GestorRecursos,
                        restricciones: List[Restriccion], archivo: str = "datos.json"):
    # archivo:es la ruta completa donde se encuentran los datos del sistema
        datos ={
            "metadata": { 
                "fecha_guardado": datetime.now().isoformat(),
                "version": "1.0",#Por si se modifica la estructura de datos posteriormente
                "total_eventos": len(gestor_eventos),
                "total_recursos": len(gestor_recursos),
                "total_restricciones": len(restricciones)
            },
            "eventos": [ evento.to_dict() for evento in gestor_eventos.eventos.values()],
            "recursos": [recurso.to_dict() for recurso in gestor_recursos.recursos.values()],
            "restricciones": Persistencia.serializar_restricciones(restricciones)
            }

        #Crear el directorio si no existe 
        directorio = os.path.dirname(archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)

        with open(archivo, 'w', encoding = 'utf-8') as f:
            json.dump(datos, f, indent = 2, ensure_ascii = False, default = str)
    
    @staticmethod
    def cargar_sistema(archivo: str = "datos.json") -> tuple:
        """Permite cargar los datos del sistema"""
        """
        Returns: tuple: (gestor_eventos, gestor_recursos, restricciones)
        Raises:
        FileNotFoundError: "El archivo no fue encontrado"
        json.JSONDecodeError: "Si el archivo no es JSON válido"

        """
        with open(archivo, 'r',encoding ='utf-8') as f:
            datos = json.load(f)

        #cargar recursos
        gestor_recursos = GestorRecursos()
        for recurso_data in datos.get("recursos", []):
            recurso_id = recurso_data.get('id')
            recurso_existente = gestor_recursos.obtener_recurso(recurso_id)
        
            if recurso_existente:
                # Actualizar recurso existente
                recurso_existente.nombre = recurso_data.get('nombre', '')
                recurso_existente.tipo = recurso_data.get('tipo', '')
                recurso_existente.capacidad = recurso_data.get('capacidad', 1)
                recurso_existente.atributos = recurso_data.get('atributos', {})
            else:
                # Crear nuevo recurso
                gestor_recursos.agregar_recurso(Recurso.from_dict(recurso_data))
            
        #cargar eventos (depende de recursos)
        gestor_eventos = GestorEventos()
        for evento_data in datos.get("eventos", []):
            recursos_evento = [] 
            for recurso_data in evento_data.get("recursos", []):
                if isinstance(recurso_data, dict):
                    # Vamos a deserializar los recursos a partir de ID
                    # Ya que si utilizamos la función Recurso.from_dict(), se crearían múltiples instancias del mismo recurso 
                    # y nos interesa que el mismo recurso físico tenga una única instancia en memoria
                    recurso_id = recurso_data.get('id')
                    recurso = gestor_recursos.obtener_recurso(recurso_id)
                    if not recurso:
                        raise ValueError(
                            f"El recurso con ID '{recurso_id}' referenciado en evento '{evento_data.get('id', 'sin id')}', "
                            "no es encontrado en el gestor de recursos"
                        )   
                    recursos_evento.append(recurso)
                else:
                    #En caso de que el recurso sea una instancia de la clase Recurso
                    #(Que no debería pasar en cadena JSON)
                    recursos_evento.append(recurso_data)

            # Vamos a actualizar los recursos(como objeto Recurso) que pertenecen al evento
            evento_data["recursos"] = recursos_evento

            #Para crear el objeto evento 
            evento = Evento.from_dict(evento_data)
            gestor_eventos.agregar_evento(evento)

        #cargar restricciones
        restricciones = Persistencia.deserializar_restricciones(datos.get("restricciones", []))
        
        return gestor_eventos, gestor_recursos, restricciones
    
    @staticmethod
    def serializar_restricciones(restricciones: List[Restriccion]) -> List[Dict[str, Any]]:
        """Convierte una lista de restricciones a diccionarios serializables"""
        resultado = []
        for restriccion in restricciones:
            if isinstance(restriccion, RestriccionCoRequisito):
                tipo = "co_requisito"
                parametros = {
                    "principal": restriccion.principal,
                    "requerido": restriccion.requerido
                }
            elif isinstance(restriccion, RestriccionExclusionMutua):
                tipo = "exclusion_mutua"
                parametros = {
                    "recurso_a":restriccion.recurso_a,
                    "recurso_b":restriccion.recurso_b
                }
            elif isinstance(restriccion, RestriccionCapacidad):
                tipo = "capacidad"
                parametros = {
                    "tipo_recurso": restriccion.tipo_recurso,
                    "capacidad_maxima": restriccion.capacidad_maxima
                }
            else:
                continue  #Restriccion desconocida, se omite
            
            resultado.append({
                "tipo": tipo,
                "parametros": parametros
            })
            
        return resultado
    
    @staticmethod
    def deserializar_restricciones(restricciones_data: List[Dict[str, Any]]) ->List[Restriccion]:
        """Reconstruye una lista de restricciones a partir de datos serializados"""
        restricciones = []
        for data in restricciones_data:
            tipo = data.get("tipo", "")
            parametros = data.get("parametros", {})
            
            if tipo == "co_requisito":
                restriccion = RestriccionCoRequisito(
                    id_recurso_principal = parametros.get("principal"),
                    id_recurso_requerido = parametros.get("requerido"))
            
            elif tipo == "exclusion_mutua":
                restriccion = RestriccionExclusionMutua(
                    id_recurso_a = parametros.get("recurso_a"),
                    id_recurso_b = parametros.get("recurso_b")
                )
            elif tipo == "capacidad":
                restriccion = RestriccionCapacidad(
                    tipo_recurso = parametros.get("tipo_recurso"),
                    capacidad_maxima = parametros.get("capacidad_maxima")
                )
            else:
                continue #tipo desconocido, se omite
            
            restricciones.append(restriccion)
            
        return restricciones
    
    @staticmethod 
    def cargar_backup(archivo_backup: str) ->tuple:
        """Permite cargar datos desde un archivo backup"""
        return Persistencia.cargar_sistema(archivo_backup)
    
    @staticmethod 
            

    def crear_backup(gestor_recursos: GestorRecursos, gestor_eventos: GestorEventos,
                     restricciones: List[Restriccion], directorio_backup: str = "backups"):
        """Crea un backup del sistema con timestamp"""
        
        # timestamp es una marca de tiempo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_backup = f"{directorio_backup}/backup_{timestamp}.json"
        # Para crear el directorio si no existe 
        if not os.path.exists(directorio_backup):
            os.makedirs(directorio_backup)
            
        Persistencia.guardar_sistema(gestor_eventos, gestor_recursos, 
                                            restricciones, archivo_backup)
        
        return archivo_backup
    
    @staticmethod
    def listar_backups(directorio_backups: str = "backups") ->List[str]:    
        # directorio_backups: str = "backups" es como otorgarle un valor por defecto? 
        if not os.path.exists(directorio_backups):
            return []     
        
        backups = []
        for archivo in os.listdir(directorio_backups):
            if archivo.startswith("backup_") and archivo.endswith(".json"):
                ruta_completa = os.path.join(directorio_backups, archivo)
                tamaño = os.path.getsize(ruta_completa) #Qué es específicamente el tamaño de una ruta
                backups.append({
                    "nombre": archivo,
                    "tamaño": tamaño,
                    "ruta": ruta_completa
                })
                
        #Ordenar los backups por nombre, siendo los primeros, los más recientes
        backups.sort(key = lambda x: x["nombre"], reverse = True)
        return backups
                            
            

            
            


        

    

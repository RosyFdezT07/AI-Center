"""
Planificador principal
"""
from __future__ import annotations
import json 
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

# Importaciones relativas desde el paquete
from dominio.recursos import Recurso, GestorRecursos, crear_recursos_predeterminados
from dominio.eventos import Evento, GestorEventos
from dominio.restricciones import Restriccion, crear_restricciones_predeterminadas, validar_restricciones
from infraestructura.persistencia import Persistencia

class Planificador:
    """Clase principal que integra todo el proceso de planificación"""
    
    def __init__(self, datos_dir :str = "datos"):
        # Si a la función no se le especifica los datos_dir, automáticamente genera el parámetro "datos" por defecto
        """Inicializa el planificador con gestor de recursos, gestor de eventos y restricciones """
        
        self.datos_dir = datos_dir
        os.makedirs(datos_dir, exist_ok = True) 
        # No lanza error si el directorio ya existe(exist_ok = True)
        
        self.gestor_recursos = GestorRecursos()
        self.gestor_eventos = GestorEventos()
        self.restricciones = crear_restricciones_predeterminadas()
        
    def cargar_recursos_iniciales(self, limpiar_existentes: bool = True):
        """Carga los recursos iniciales del sistema (predeterminados)"""
        if limpiar_existentes:
            self.gestor_recursos = GestorRecursos()  # Limpiar antes de cargar
        
        recursos_predeterminados = crear_recursos_predeterminados()
        for recurso in recursos_predeterminados.recursos.values():  # crear_recursos_predeterminados() devuelve GestorRecursos
            self.gestor_recursos.agregar_recurso(recurso)
        
        print(f" Cargados {len(self.gestor_recursos)} recursos predeterminados")
            

    def planificar_evento(
        self,
        nombre: str,
        inicio: datetime,
        fin: datetime,
        recursos_seleccionados: Dict[str, int],
        tipo: str,
        descripcion: str = "",
        prioridad: int = 1,
        buscar_hueco_si_ocupado: bool = False
    ) ->Dict[str, Any]:
        """
        Intenta planificar un nuevo evento
        Return: Resultado de la operación 
        """
        resultado = {
            "success": False,
            "message": "",
            "evento": None,
            "detalles": {}
        }
            
        try:
            # Validar parámetros básicos
            ahora = datetime.now()
            fecha_minima = datetime(2020, 1, 1)
            año_actual = datetime.now().year
            
            if inicio >= fin:
                resultado['message'] = 'La fecha de inicio debe ser anterior a la de fin'
                return resultado
            
            if fin - inicio > timedelta(days =7):
                resultado["message"] = 'Los eventos no pueden durar más de 7 días'
                return resultado
            
            if inicio < ahora - timedelta(minutes=5):
                resultado['message'] = 'La fecha de inicio no puede ser en el pasado(a menos que sea 5 minutos antes de la fecha actual)'
                return resultado
            
            if inicio < fecha_minima:
                resultado['message'] = f'La fecha debe ser posterior al {fecha_minima.year}'
                return resultado
            
            
            if inicio.year < 2000 or inicio.year > año_actual + 10:
                resultado['message'] = f'El año ({inicio.year}) no es válido. Debe estar entre 2000 y {año_actual + 10}'
                return resultado
            
            if fin.year < 2000 or fin.year > año_actual + 10:
                resultado['message'] = f'El año ({fin.year}) no es válido. Debe estar entre 2000 y {año_actual + 10}'
                return resultado

            
            # Obtener recursos
            recursos = []
            for recurso_id, cantidad in recursos_seleccionados.items():
                recurso = self.gestor_recursos.obtener_recurso(recurso_id)
                if not recurso:
                    resultado["message"] = f"Recurso {recurso_id} no encontrado"
                    return resultado
                
                if cantidad > recurso.capacidad: 
                    resultado["message"] = "La cantidad solicitada supera la capacidad" 
                    return resultado
                
                # Agregar el recurso la cantidad de veces especificada
                for i in range(cantidad):
                    recursos.append(recurso)
                    
            # Crear evento temporal para validaciones 
            evento_temp =Evento(
                nombre = nombre,
                inicio = inicio, 
                fin = fin,
                recursos = recursos,
                tipo = tipo,
                descripcion = descripcion,
                prioridad = prioridad,
            )
            
            # Validar restricciones
            es_valido, errores = validar_restricciones(recursos, evento_temp, self.restricciones)
            if not es_valido:
                resultado["message"] = f'Violación de restricciones: {", ".join(errores)}'
                return resultado
            
            # Verificar disponibilidad
            errores = []

            # Verificar Conflictos de Recursos (Capacidad/Pools)
            sin_conflictos, errores_conflictos = self.verificar_conflictos(evento_temp)
            if not sin_conflictos:
                errores.extend(errores_conflictos)
                if buscar_hueco_si_ocupado:
                    # Buscar hueco automáticamente
                    return self.buscar_hueco_automático(
                        nombre, inicio, fin, recursos, tipo, descripcion, prioridad
                        )
                else:
                    resultado["message"] = f"{errores}"
                    return resultado  
            
            # Crear y agregar evento
            evento = Evento(
                nombre = nombre,
                inicio = inicio,
                fin = fin,
                recursos = recursos,
                tipo = tipo,
                descripcion = descripcion, 
                prioridad = prioridad
            ) 
            
            if self.gestor_eventos.agregar_evento(evento):
                resultado["success"] = True
                resultado["message"] = "Evento agregado exitosamente"
                resultado["evento"] = evento
                resultado["detalles"] = {
                    'id': evento.id,
                    'duracion_horas': evento.duracion_horas,
                    'recursos_asignados': [r.nombre for r in recursos]
                }
            else: 
                resultado["message"] = "Error al agregar el evento"        
                
        except Exception as e:
            resultado["message"] = f"Error: {str(e)}"
        
        return resultado 
    
    def verificar_conflictos(self, nuevo_evento: Evento) -> Tuple[bool, List[str]]:
        errores = []
        
        # Agrupar la demanda del nuevo evento
        demanda_nuevo = {}
        for r in nuevo_evento.recursos:
            demanda_nuevo[r.id] = demanda_nuevo.get(r.id, 0) + 1
            
        # Verificar cada recurso solicitado
        for id_recurso, cantidad_solicitada in demanda_nuevo.items():
            recurso = self.gestor_recursos.obtener_recurso(id_recurso)
            if not recurso:
                errores.append(f"Recurso {id_recurso} no existe.")
                continue

            # Obtener solo los eventos que usan este recurso y se solapan con el nuevo
            eventos_interes = [
                ev for ev in self.gestor_eventos.eventos.values()
                if ev.id != nuevo_evento.id 
                and ev.se_solapa_con(nuevo_evento)
                and any(r.id == id_recurso for r in ev.recursos)
            ]

            # Creamos una lista de puntos de tiempo importantes (inicio y fin de cada evento)
            # para ver cuántos están activos simultáneamente.
            puntos_tiempo = []
            
            # Añadimos los eventos existentes
            for ev in eventos_interes:
                # Contamos cuántas unidades de este recurso usa este evento
                cantidad_uso = sum(1 for r in ev.recursos if r.id == id_recurso)
                # Solo nos importa el intervalo que intersecta con el nuevo evento
                inicio_real = max(ev.inicio, nuevo_evento.inicio)
                fin_real = min(ev.fin, nuevo_evento.fin)
                
                if inicio_real < fin_real:
                    puntos_tiempo.append((inicio_real, cantidad_uso))  # Sumar al inicio
                    puntos_tiempo.append((fin_real, -cantidad_uso))    # Restar al final
            
            # Añadimos el nuevo evento
            puntos_tiempo.append((nuevo_evento.inicio, cantidad_solicitada))
            puntos_tiempo.append((nuevo_evento.fin, -cantidad_solicitada))
            
            # Ordenamos por fecha
            puntos_tiempo.sort(key=lambda x: x[0])
            
            # Simulamos el uso a lo largo del tiempo
            uso_actual = 0
            max_uso_detectado = 0
            
            for _, cambio in puntos_tiempo:
                uso_actual += cambio
                if uso_actual > max_uso_detectado:
                    max_uso_detectado = uso_actual
                    
            if max_uso_detectado > recurso.capacidad:
                errores.append(
                    f"Capacidad excedida para '{recurso.nombre}': "
                    f"Se requieren {max_uso_detectado} simultáneos, capacidad máxima {recurso.capacidad}."
                )

        return len(errores) == 0, errores
    
    def buscar_hueco_automático(
        self,
        nombre: str,
        inicio_original: datetime,
        fin_original: datetime,
        recursos: List[Recurso],
        tipo: str, 
        descripcion: str,
        prioridad: int = 1
        
    ) ->Dict[str, Any]:
        
        """Busca automáticamente un hueco disponible para el evento"""
        duracion = fin_original - inicio_original 
        tiempo_actual = inicio_original
        
        # Buscar en los próximos 7 días
        limite_busqueda = tiempo_actual + timedelta(days=7)
        while tiempo_actual < limite_busqueda:
            # Intenta para cada 10 minutos 
            tiempo_intento = tiempo_actual
            tiempo_fin_intento = tiempo_actual + duracion
        
            # Crear evento de prueba
            evento_prueba = Evento(
                nombre = nombre,
                inicio = tiempo_intento,
                fin = tiempo_fin_intento,
                recursos = recursos,
                tipo = tipo,
                descripcion = descripcion,
                prioridad = prioridad
            )
        
            # Verificar si hay conflicto 
            sin_conflictos, errores_conflictos = self.verificar_conflictos(evento_prueba)
            
            if sin_conflictos:
                # También verificar restricciones 
                es_valido, mensajes_error = validar_restricciones(recursos, evento_prueba, self.restricciones)
                if es_valido:
                    # Crear el evento y agregarlo de forma definitiva
                    evento = Evento(
                        nombre = nombre,
                        inicio = tiempo_intento,
                        fin = tiempo_fin_intento,
                        recursos = recursos,
                        tipo = tipo,
                        descripcion = descripcion,
                        prioridad = prioridad
                    )
                    
                    if self.gestor_eventos.agregar_evento(evento):
                        return {
                            'success': True,
                            'message': f"Evento planificado automáticamente en el hueco encontrado",
                            'detalles':{
                                'id': evento.id,
                                'inicio_original': inicio_original,
                                'inicio_asignado': tiempo_intento,
                                'duracion_horas': evento.duracion_horas
                                
                            }
                        }
            # Avanzar 10 minutos
            tiempo_actual += timedelta(minutes=10)
            
        return {
            'success': False,
            'message': f"No se encontró hueco disponible en los próximos 7 días"
        }
        
    def buscar_hueco_disponible(self, recursos_ids, duracion_horas, inicio_busqueda=None, dias=7):
        """
        Busca huecos disponibles para un conjunto de recursos.
        Returns:
            Lista de dicts con {'inicio': datetime, 'fin': datetime, 'duracion_horas': float}
        """
        # Validar entrada
        if inicio_busqueda is None:
            inicio_busqueda = datetime.now()
        
        # Calcular límite 
        limite_final = inicio_busqueda + timedelta(days=dias)
        
        # Obtener recursos
        recursos = []
        for recurso_id in recursos_ids:
            recurso = self.gestor_recursos.obtener_recurso(recurso_id)
            if recurso:
                recursos.append(recurso)
        
        # Si no hay recursos válidos, retornar vacío
        if not recursos:
            return []
        
        # Calcular duración 
        duracion = timedelta(hours=duracion_horas)
        huecos = []
        tiempo_actual = inicio_busqueda
        
        # Búsqueda inteligente: mientras quepa un hueco completo
        while tiempo_actual + duracion <= limite_final:
            tiempo_fin = tiempo_actual + duracion
            
            # Crear evento de prueba
            evento_prueba = Evento(
                nombre="prueba_hueco",
                inicio=tiempo_actual,
                fin=tiempo_fin,
                recursos=recursos,
                tipo="entrenamiento"
            )
            
            # Verificar conflictos
            sin_conflictos, errores = self.verificar_conflictos(evento_prueba)
            
            if sin_conflictos:
                # Validar restricciones
                es_valido, mensajes_error = validar_restricciones(
                    recursos, evento_prueba, self.restricciones
                )
                
                if es_valido:
                    # Agregar hueco disponible
                    huecos.append({
                        'inicio': tiempo_actual,
                        'fin': tiempo_fin,
                        'duracion_horas': duracion_horas
                    })
                    
            # Si hay conflicto o no es válido, avanzar 10 minutos
            tiempo_actual += timedelta(minutes=10)
        
        return huecos
        
    def listar_eventos(self, dias: int = 1) ->List[Evento]:
        """Organiza los próximos eventos"""
        
        ahora = datetime.now()
        fin_rango = ahora + timedelta(days=dias)
        
        eventos = self.gestor_eventos.obtener_por_rango_fecha(ahora, fin_rango)
        # Ordenar los eventos por fecha de inicio( el más antiguo es el que aparece de primero)
        eventos.sort(key=lambda e: e.inicio)
        
        return eventos
    
    def listar_recursos(self) ->List[Recurso]:
        """Lista todos los recursos disponibles"""
        return list(self.gestor_recursos.recursos.values())
    
    def obtener_agenda_recurso(self, recurso_id: str, dias: int = 7) -> List[Evento]:
        """
        Devuelve todos los eventos planificados en los siguientes días, 
        que utilizan un recurso específico
        """
        ahora = datetime.now()
        fin_rango = ahora + timedelta(days = dias)
        
        recurso = self.gestor_recursos.obtener_recurso(recurso_id)
        if not recurso:
            return []
        
        # Obtener los eventos que tienen el recurso
        eventos_recurso = self.gestor_eventos.obtener_por_recurso(recurso)
        
        # Filtrar los eventos por rango de fecha
        eventos_filtrados = [e for e in eventos_recurso 
                             if ahora <= e.inicio <= fin_rango]
        
        # Ordenar los eventos filtrados por fecha
        eventos_filtrados.sort(key=lambda e: e.inicio)
        
        return eventos_filtrados
    
    def eliminar_evento(self, evento_id) ->bool:
        """Elimina el evento por ID"""
        return self.gestor_eventos.eliminar_evento(evento_id)
    
    def __str__(self):
        """Representación del planificador"""
        return (f"Planificador(recursos: {len(self.gestor_recursos)}," 
               f"eventos: {len(self.gestor_eventos)})") 
        
    def cargar_datos(self, archivo: str = "datos.json") ->bool:
        """
        Carga los datos usando la clase Persistencia
        Returns:
            True si tuvo éxito al cargar
        """
        ruta_archivo = os.path.join(self.datos_dir, archivo)
        
        # Intentar cargar con Persistencia
        if os.path.exists(ruta_archivo):
        
            try:
                gestor_eventos, gestor_recursos, restricciones = Persistencia.cargar_sistema(ruta_archivo)
                self.gestor_eventos = gestor_eventos
                self.gestor_recursos = gestor_recursos
                
                # Si no hay restricciones, crear predeterminadas
                if not restricciones or len(restricciones) == 0:
                    print(" No se encontraron restricciones, creando predeterminadas...")
                    restricciones = crear_restricciones_predeterminadas()
                
                self.restricciones = restricciones
                print(f" Datos cargados desde {archivo} - {len(restricciones)} restricciones")
                return True
                
            except Exception as e:
                print(f" Error al cargar datos: {e}")
                # Continuar con formato antiguo
        
        # Si no existe o falla, intentar cargar formato antiguo para compatibilidad
        archivo_antiguo = "datos.json"
        ruta_antigua = os.path.join(self.datos_dir, archivo_antiguo)
        
        if os.path.exists(ruta_antigua):
            try:
                # Cargar formato antiguo
                with open(ruta_antigua, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    
                # Limpiar antes de cargar
                self.gestor_recursos = GestorRecursos()
                self.gestor_eventos = GestorEventos()
                
                # Cargar recursos
                if 'recursos' in datos:
                    self.gestor_recursos.cargar_desde_lista(datos['recursos'])
                
                # Cargar eventos (necesita reconstruir referencias a recursos)
                if 'eventos' in datos:
                    recursos_dict = {r.id: r for r in self.gestor_recursos.recursos.values()} 
                    self.gestor_eventos.cargar_desde_lista_con_recurso(datos['eventos'], recursos_dict)
                
                # Las restricciones se mantienen como predeterminadas
                print(f"Datos cargados desde formato antiguo {archivo_antiguo}")
                
                #  Auto-migrar al nuevo formato
                self.guardar_datos(archivo)  # Guardar en nuevo formato
                print(f" Datos migrados automáticamente a {archivo}")
                
                return True
            except Exception as e:
                print(f"Error al cargar formato antiguo: {e}")
        
        # Si no existe ningún archivo, cargar recursos predeterminados
        self.cargar_recursos_iniciales()
        print(" Cargados recursos predeterminados (sin datos previos)")
        return False
        
    def guardar_datos(self, archivo: str = "datos.json") -> bool:
        """
        Guardar los datos usando la clase Persistencia
        """
        ruta_archivo = os.path.join(self.datos_dir, archivo)
        
        try:
            # Usar Persistencia para guardar
            Persistencia.guardar_sistema(
                self.gestor_eventos,
                self.gestor_recursos,
                self.restricciones,
                ruta_archivo
            )
            return True
        except Exception as e:
            print(f"Error al guardar datos con Persistencia: {e}")
            return False
        

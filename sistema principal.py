# sistema.py
class SistemaCentroIA:
    def __init__(self):
        self.gestor_recursos = GestorRecursos()
        self.gestor_eventos = GestorEventos()
        self.planificador = Planificador()
        self.restricciones = []
        self._cargar_recursos_predeterminados()
        self._cargar_restricciones_predeterminadas()
    
    def planificar_evento(self, nombre, inicio, fin, recursos_ids, tipo):
        # 1. Convertir IDs a objetos Recurso
        # 2. Crear evento
        # 3. Validar con planificador
        # 4. Si válido, agregar a gestor_eventos
        pass
    
    def buscar_hueco(self, duracion_horas, recursos_ids, tipo_evento):
        # Usar planificador.buscar_proximo_hueco
        pass
    
    def eliminar_evento(self, id_evento):
        # Liberar recursos del evento
        pass
    
    def obtener_agenda_recurso(self, id_recurso):
        # Filtrar eventos que usan ese recurso
        pass
# planificador.py
class Planificador:
    def __init__(self):
        self.margen_seguridad = timedelta(minutes=15)
    
    def validar_evento(self, evento, eventos_existentes, restricciones):
        # 1. Validar conflictos de tiempo
        # 2. Validar restricciones
        # 3. Retornar resultado
        pass
    
    def buscar_proximo_hueco(self, duracion, recursos_necesarios, 
                            eventos_existentes, restricciones):
        # Algoritmo de búsqueda de huecos
        # Buscar en ventanas de tiempo
        pass
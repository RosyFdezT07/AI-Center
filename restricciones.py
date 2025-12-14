# restricciones.py
class Restriccion:
    def validar(self, evento, eventos_existentes): pass

class RestriccionCoRequisito(Restriccion):
    def __init__(self, recurso_principal, recursos_requeridos):
        # Ej: GPU requiere Investigador
        pass

class RestriccionExclusionMutua(Restriccion):
    def __init__(self, recurso1, recurso2, motivo):
        # Ej: Dos clusters no pueden usarse juntos
        pass

class RestriccionCapacidad(Restriccion):
    def __init__(self, tipo_recurso, capacidad_maxima):
        # Ej: Máximo 2 investigadores por evento
        pass
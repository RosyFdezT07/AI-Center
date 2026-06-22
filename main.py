"""
 Punto de entrada oficial para la evaluación del proyecto
 Este script actúa como un adaptador para cumplir con el requisito del sistema
 automatizado de MatCom, el cual busca un archivo "main.py". Como la interfaz 
 gráfica está desarrollada en Streamlit (que requiere un comando especial),
 este archivo redirige la ejecución hacia "app.py".

"""
import os
if __name__ == "__main__":
    # Mensaje en la terminal para confirmar que el script arrancó 
    print("Iniciando el Planificador Inteligente de Eventos...")
    
    # Invoca al sistema operativo para levantar el servidor de Streamlit
    os.system("streamlit run app.py")
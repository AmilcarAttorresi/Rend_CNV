
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import time
from urllib.parse import urljoin

def descargar_planilla_cnv():
    """
    Descarga la planilla más reciente de valores diarios de la CNV
    """
    url_base = "https://www.cnv.gov.ar/SitioWeb/FondosComunesInversion/CuotaPartes"
    
    try:
        # Obtener la página principal
        response = requests.get(url_base)
        response.raise_for_status()
        
        # Parsear el HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Encontrar el primer enlace (más reciente)
        enlaces = soup.find_all('a', href=True)
        enlace_mas_reciente = None
        
        for enlace in enlaces:
            if 'jun 2025' in enlace.text or 'may 2025' in enlace.text:
                enlace_mas_reciente = enlace['href']
                fecha_documento = enlace.text.strip()
                break
        
        if not enlace_mas_reciente:
            print("No se encontró enlace de descarga")
            return None, None
            
        # Construir URL completa si es necesaria
        if not enlace_mas_reciente.startswith('http'):
            url_descarga = urljoin(url_base, enlace_mas_reciente)
        else:
            url_descarga = enlace_mas_reciente
        
        # Descargar el archivo
        print(f"Descargando planilla del {fecha_documento}...")
        response_archivo = requests.get(url_descarga)
        response_archivo.raise_for_status()
        
        # Guardar temporalmente
        nombre_temp = f"valores_diarios_temp_{datetime.now().strftime('%Y%m%d')}.xlsx"
        ruta_temp = os.path.join(os.path.expanduser("~/Downloads"), nombre_temp)
        
        with open(ruta_temp, 'wb') as f:
            f.write(response_archivo.content)
        
        print(f"Archivo descargado: {ruta_temp}")
        return ruta_temp, fecha_documento
        
    except Exception as e:
        print(f"Error al descargar: {e}")
        return None, None

def procesar_excel_y_crear_resumen(ruta_archivo, fecha_documento):
    """
    Procesa el archivo Excel y crea un resumen con nombres de fondos y rendimientos
    """
    try:
        # Leer el archivo Excel
        print("Procesando archivo Excel...")
        df = pd.read_excel(ruta_archivo)
        
        # Verificar que existan las columnas necesarias
        if len(df.columns) < 10:  # Columna J sería la índice 9
            print("El archivo no tiene suficientes columnas")
            return False
        
        # Extraer columna A (nombres de fondos) y columna J (rendimientos)
        nombres_fondos = df.iloc[:, 0]  # Columna A (índice 0)
        rendimientos = df.iloc[:, 9]    # Columna J (índice 9)
        
        # Crear DataFrame con los datos extraídos
        datos_resumen = pd.DataFrame({
            'Nombre_Fondo': nombres_fondos,
            'Rendimiento': rendimientos
        })
        
        # Limpiar datos (remover filas vacías)
        datos_resumen = datos_resumen.dropna(subset=['Nombre_Fondo'])
        
        # Crear nombre del archivo de salida
        fecha_limpia = fecha_documento.replace(' ', '_').replace('.', '')
        nombre_salida = f"Resumen_Fondos_Rendimientos_{fecha_limpia}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        ruta_salida = os.path.join(os.path.expanduser("~/Downloads"), nombre_salida)
        
        # Guardar el resumen
        datos_resumen.to_excel(ruta_salida, index=False, sheet_name='Resumen_Rendimientos')
        
        print(f"Resumen creado exitosamente: {ruta_salida}")
        print(f"Total de fondos procesados: {len(datos_resumen)}")
        
        # Mostrar preview de los primeros 5 registros
        print("\nPreview de los datos:")
        print(datos_resumen.head().to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        return False
    
    finally:
        # Limpiar archivo temporal
        try:
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
                print("Archivo temporal eliminado")
        except:
            pass

def main():
    """
    Función principal que ejecuta todo el proceso
    """
    print("=== AUTOMATIZACIÓN VALORES DIARIOS CNV ===")
    print(f"Iniciando proceso: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Paso 1: Descargar la planilla más reciente
    ruta_archivo, fecha_documento = descargar_planilla_cnv()
    
    if not ruta_archivo:
        print("No se pudo descargar la planilla. Proceso terminado.")
        return
    
    # Paso 2: Procesar y crear resumen
    exito = procesar_excel_y_crear_resumen(ruta_archivo, fecha_documento)
    
    if exito:
        print("\n✅ Proceso completado exitosamente!")
    else:
        print("\n❌ Hubo errores en el procesamiento")
    
    print(f"Proceso finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()


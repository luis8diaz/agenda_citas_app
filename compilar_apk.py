import os
import subprocess
import sys

print("=== INICIANDO COMPILADOR DIRECTO DE APK (CORREGIDO) ===")
sdk_path = r"D:\SDK"
os.environ["ANDROID_HOME"] = sdk_path

if not os.path.exists(sdk_path):
    print(f"ERROR: No se encuentra el SDK en {sdk_path}")
    sys.exit(1)

print(f"SDK detectado en: {sdk_path}")

# Ejecutar flet build apk directamente usando el comando del sistema
try:
    print("Ejecutando flet build apk...")
    resultado = subprocess.run(["flet", "build", "apk"], shell=True)
    
    if resultado.returncode == 0:
        print("¡APK GENERADO EXITOSAMENTE!")
    else:
        print("El comando directo requiere inicializar src. Creando estructura...")
        subprocess.run(["flet", "create", "."], shell=True)
        print("Estructura creada. Reintentando compilación...")
        subprocess.run(["flet", "build", "apk"], shell=True)
except Exception as e:
    print(f"Error: {e}")

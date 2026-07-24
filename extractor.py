import subprocess
import os

# 1. Leer las URLs del archivo original
if os.path.exists('urls.txt'):
    with open('urls.txt', 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
else:
    print("❌ No se encontró urls.txt")
    urls = []

resultados = []

# 2. Procesar cada URL
for url in urls:
    try:
        print(f"🔄 Procesando: {url}")
        # AUMENTADO a 60s: GitHub Actions a veces tiene latencia de red. 30s puede ser muy justo.
        cmd = ['yt-dlp', '--no-warnings', '--print', '%(title)s | %(url)s', url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and result.stdout.strip():
            resultados.append(result.stdout.strip())
            print(f"✅ Éxito")
        else:
            # Si falla, NO lo agregamos a la lista para no ensuciar el archivo final 
            # y evitar que el HTML intente reproducir una línea de error.
            print(f"⚠️ Omitido (falló la extracción): {url}")
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ Timeout (60s) agotado para: {url}")
    except Exception as e:
        print(f"❌ Excepción en {url}: {e}")

# 3. Guardar solo las URLs válidas
with open('urls_frescas.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(resultados))

print(f"🎉 Completado. {len(resultados)} URLs válidas guardadas en urls_frescas.txt")

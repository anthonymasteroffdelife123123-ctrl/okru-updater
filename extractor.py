import subprocess
import os
import re

if os.path.exists('urls.txt'):
    with open('urls.txt', 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
else:
    print("❌ No se encontró urls.txt")
    urls = []

resultados = []

for url in urls:
    try:
        print(f"🔄 Procesando: {url}")
        
        # 🔥 DETECTAR SI ES VK O OK.RU
        if 'vk.com' in url or 'vkvideo.ru' in url:
            # Es VK - usar yt-dlp con opciones especiales
            cmd = [
                'yt-dlp', 
                '--no-warnings', 
                '--print', '%(title)s | %(url)s',
                '--add-header', 'User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                url
            ]
        else:
            # Es OK.ru - usar el comando normal
            cmd = ['yt-dlp', '--no-warnings', '--print', '%(title)s | %(url)s', url]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # Limpiar la salida por si hay caracteres raros
            output = result.stdout.strip()
            if output:
                resultados.append(output)
                print(f"✅ Éxito: {output[:50]}...")
            else:
                resultados.append(f"❌ ERROR: {url} (sin salida)")
        else:
            # 🔥 INTENTAR CON MÉTODO ALTERNATIVO PARA VK
            if 'vk.com' in url or 'vkvideo.ru' in url:
                print(f"⚠️ Falló yt-dlp, intentando método alternativo para VK...")
                # Usar cookies si existen
                if os.path.exists('cookies.txt'):
                    cmd_alt = [
                        'yt-dlp',
                        '--no-warnings',
                        '--print', '%(title)s | %(url)s',
                        '--cookies', 'cookies.txt',
                        url
                    ]
                    result_alt = subprocess.run(cmd_alt, capture_output=True, text=True, timeout=60)
                    if result_alt.returncode == 0 and result_alt.stdout.strip():
                        resultados.append(result_alt.stdout.strip())
                        print(f"✅ Éxito con cookies")
                        continue
            
            # Si todo falla, guardar error
            error_msg = result.stderr.strip()[:200] if result.stderr else "Error desconocido"
            resultados.append(f"❌ ERROR: {url} | {error_msg}")
            print(f"❌ Falló: {error_msg}")
            
    except subprocess.TimeoutExpired:
        resultados.append(f"❌ TIMEOUT: {url}")
        print(f"⏰ Timeout: {url}")
    except Exception as e:
        resultados.append(f"❌ FALLO: {url} | {str(e)[:100]}")
        print(f"❌ Error: {e}")

# Guardar resultados
with open('urls_frescas.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(resultados))

print(f"🎉 Completado. {len(resultados)} entradas procesadas.")

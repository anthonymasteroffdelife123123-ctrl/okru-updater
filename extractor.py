import subprocess
import os
import re
import json
from datetime import datetime

def extraer_id(url):
    """Extrae ID de OK.ru o VK"""
    # OK.ru
    match = re.search(r'ok\.ru/video(?:embed)?/(\d+)', url)
    if match:
        return match.group(1)
    # VK
    match = re.search(r'vk(?:video)?\.ru/video[_-](\d+_\d+)', url)
    if match:
        return match.group(1)
    match = re.search(r'vk\.com/video[_-](\d+_\d+)', url)
    if match:
        return match.group(1)
    return None

# ==========================================
# LEER URLs
# ==========================================
if os.path.exists('urls.txt'):
    with open('urls.txt', 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
else:
    print("❌ No se encontró urls.txt")
    urls = []

# ==========================================
# LEER JSON EXISTENTE
# ==========================================
json_file = 'info.json'
json_data = {}
if os.path.exists(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        print(f"📄 JSON cargado: {len(json_data)} entradas")
    except:
        print("⚠️ Error al leer JSON, creando nuevo")
        json_data = {}

# ==========================================
# PROCESAR CADA URL
# ==========================================
resultados = []
ids_procesados = set()

for url in urls:
    video_id = extraer_id(url)
    
    if not video_id:
        print(f"⚠️ No se pudo extraer ID de: {url}")
        resultados.append(f"❌ ERROR: {url}")
        continue
    
    if video_id in ids_procesados:
        print(f"ℹ️ ID {video_id} ya procesado, saltando...")
        continue
    ids_procesados.add(video_id)
    
    print(f"🔄 Procesando ID: {video_id}")
    
    try:
        # 🔥 DETECTAR SI ES VK O OK.RU
        if 'vk.com' in url or 'vkvideo.ru' in url:
            cmd = [
                'yt-dlp', 
                '--no-warnings', 
                '--print', '%(title)s | %(url)s',
                '--add-header', 'User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                url
            ]
        else:
            cmd = ['yt-dlp', '--no-warnings', '--print', '%(title)s | %(url)s', url]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and result.stdout.strip():
            output = result.stdout.strip()
            partes = output.split(' | ', 1)
            titulo = partes[0] if len(partes) > 0 else "Sin título"
            url_directa = partes[1] if len(partes) > 1 else url
            
            # 🔥 ACTUALIZAR JSON
            if video_id in json_data:
                # Solo actualizar URL directa, mantener el resto
                json_data[video_id]['url_directa'] = url_directa
                json_data[video_id]['actualizado'] = datetime.now().isoformat()
                print(f"✅ JSON actualizado: {video_id}")
            else:
                # Crear entrada nueva
                json_data[video_id] = {
                    'titulo': titulo,
                    'url_directa': url_directa,
                    'url_original': url,
                    'actualizado': datetime.now().isoformat()
                }
                print(f"✅ Nueva entrada JSON: {video_id}")
            
            resultados.append(output)
            print(f"✅ Éxito: {titulo[:50]}...")
            
        else:
            # 🔥 INTENTAR CON MÉTODO ALTERNATIVO PARA VK
            if 'vk.com' in url or 'vkvideo.ru' in url:
                print(f"⚠️ Falló yt-dlp, intentando método alternativo...")
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
                        output_alt = result_alt.stdout.strip()
                        partes_alt = output_alt.split(' | ', 1)
                        titulo_alt = partes_alt[0] if len(partes_alt) > 0 else "Sin título"
                        url_directa_alt = partes_alt[1] if len(partes_alt) > 1 else url
                        
                        # Actualizar JSON con el resultado alternativo
                        if video_id in json_data:
                            json_data[video_id]['url_directa'] = url_directa_alt
                            json_data[video_id]['actualizado'] = datetime.now().isoformat()
                        else:
                            json_data[video_id] = {
                                'titulo': titulo_alt,
                                'url_directa': url_directa_alt,
                                'url_original': url,
                                'actualizado': datetime.now().isoformat()
                            }
                        
                        resultados.append(output_alt)
                        print(f"✅ Éxito con cookies")
                        continue
            
            # Si todo falla, guardar error
            error_msg = result.stderr.strip()[:200] if result.stderr else "Error desconocido"
            resultados.append(f"❌ ERROR: {url} | {error_msg}")
            print(f"❌ Falló: {error_msg}")
            
            # Guardar en JSON con URL original si falla
            if video_id not in json_data:
                json_data[video_id] = {
                    'titulo': f"Video {video_id}",
                    'url_directa': url,
                    'url_original': url,
                    'actualizado': datetime.now().isoformat()
                }
            
    except subprocess.TimeoutExpired:
        resultados.append(f"❌ TIMEOUT: {url}")
        print(f"⏰ Timeout: {url}")
        if video_id not in json_data:
            json_data[video_id] = {
                'titulo': f"Video {video_id}",
                'url_directa': url,
                'url_original': url,
                'actualizado': datetime.now().isoformat()
            }
    except Exception as e:
        resultados.append(f"❌ FALLO: {url} | {str(e)[:100]}")
        print(f"❌ Error: {e}")
        if video_id not in json_data:
            json_data[video_id] = {
                'titulo': f"Video {video_id}",
                'url_directa': url,
                'url_original': url,
                'actualizado': datetime.now().isoformat()
            }

# ==========================================
# GUARDAR ARCHIVOS
# ==========================================

# Guardar urls_frescas.txt
with open('urls_frescas.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(resultados))

# Guardar JSON actualizado
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)

# ==========================================
# ESTADÍSTICAS
# ==========================================
print(f"\n🎉 Completado. {len(resultados)} entradas procesadas.")
print(f"📄 JSON actualizado con {len(json_data)} entradas.")

# Mostrar cuántas URLs directas se actualizaron
actualizadas = sum(1 for v in json_data.values() if 'url_directa' in v)
print(f"🔗 URLs directas disponibles: {actualizadas}")

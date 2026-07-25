import subprocess
import os
import json
from datetime import datetime
import re

def extraer_titulo(url):
    """Extrae el título de una URL con yt-dlp"""
    try:
        cmd = ['yt-dlp', '--no-warnings', '--print', '%(title)s', url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return None
    except:
        return None

def procesar_categoria(categoria):
    """Procesa todas las URLs de una categoría"""
    categoria_path = os.path.join('categorias', categoria)
    urls_file = os.path.join(categoria_path, 'urls.txt')
    
    if not os.path.exists(urls_file):
        print(f"❌ No se encontró {urls_file}")
        return []
    
    # Leer URLs
    with open(urls_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"📂 {categoria}: {len(urls)} URLs encontradas")
    
    resultados = []
    urls_procesadas = 0
    
    for url in urls:
        try:
            print(f"🔄 Procesando {categoria}: {url[:50]}...")
            
            # Extraer título
            titulo = extraer_titulo(url)
            
            # Extraer ID
            video_id = None
            match = re.search(r'ok\.ru/video/(\d+)', url)
            if match:
                video_id = match.group(1)
            else:
                match = re.search(r'ok\.ru/videoembed/(\d+)', url)
                if match:
                    video_id = match.group(1)
            
            if titulo and video_id:
                # Guardar JSON
                nombre_base = re.sub(r'[^a-zA-Z0-9]', '_', titulo)[:50]
                nombre_json = f"{nombre_base}.json"
                json_path = os.path.join(categoria_path, nombre_json)
                
                datos = {
                    'video_id': video_id,
                    'titulo': titulo,
                    'url': url,
                    'fecha_actualizacion': datetime.now().isoformat(),
                    'categoria': categoria,
                    'ultima_verificacion': datetime.now().isoformat()
                }
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(datos, f, indent=2, ensure_ascii=False)
                
                resultados.append(f"{titulo} | {url}")
                urls_procesadas += 1
                print(f"✅ JSON guardado: {nombre_json}")
            else:
                print(f"⚠️ No se pudo extraer título/ID para: {url}")
                # Si no se puede extraer, igual guardamos la URL
                resultados.append(url)
                urls_procesadas += 1
                
        except Exception as e:
            print(f"❌ Error en {url}: {e}")
            resultados.append(url)
            urls_procesadas += 1
    
    # Guardar resultados
    output_file = os.path.join(categoria_path, 'urls_frescas.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(resultados))
    
    print(f"✅ {categoria}: {urls_procesadas}/{len(urls)} URLs procesadas")
    return resultados

def main():
    print("🚀 Iniciando procesamiento de categorías...")
    
    # Verificar que existe la carpeta categorias
    if not os.path.exists('categorias'):
        print("❌ No existe la carpeta 'categorias'")
        return
    
    # Obtener todas las categorías
    categorias = [d for d in os.listdir('categorias') 
                  if os.path.isdir(os.path.join('categorias', d))]
    
    if not categorias:
        print("❌ No hay categorías para procesar")
        return
    
    print(f"📁 Categorías encontradas: {', '.join(categorias)}")
    
    total_procesadas = 0
    for categoria in categorias:
        print(f"\n{'='*50}")
        print(f"📁 Procesando categoría: {categoria}")
        print(f"{'='*50}")
        resultados = procesar_categoria(categoria)
        total_procesadas += len(resultados)
    
    print(f"\n{'='*50}")
    print(f"🎉 ¡PROCESO COMPLETADO!")
    print(f"📊 Total URLs procesadas: {total_procesadas}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()

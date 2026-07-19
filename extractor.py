import subprocess
import os

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
        cmd = ['yt-dlp', '--no-warnings', '--print', '%(title)s | %(url)s', url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            resultados.append(result.stdout.strip())
            print(f"✅ Éxito")
        else:
            resultados.append(f"❌ ERROR: {url}")
    except Exception as e:
        resultados.append(f"❌ FALLO: {url}")

with open('urls_frescas.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(resultados))

print("🎉 Completado. Archivo urls_frescas.txt generado.")

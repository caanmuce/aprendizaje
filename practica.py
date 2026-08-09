import requests
from bs4 import BeautifulSoup, Tag
import urllib
url= "https://elenemigos.com/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
respuesta = requests.get(url, headers=headers, timeout=10)

url_base = "https://elenemigos.com"  
PAGINAS_A_RASPAR = (
    5  
)

juegos_totales = []

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for pagina in range(1, PAGINAS_A_RASPAR + 1):
    url_pagina = f"{url_base}/?order=last_update&page={pagina}"
    print(f"🔎 Raspando página {pagina}: {url_pagina}")

    respuesta_pagina = requests.get(url_pagina, headers=headers, timeout=10)

    if respuesta_pagina.status_code == 200:
        soup=BeautifulSoup(respuesta_pagina.text, 'html.parser')

        tarjetas_juego = soup.find_all('div', class_='game-card')  

        for juego in tarjetas_juego:
            enlace_tag = juego.find('a', href=True)
            enlace_relativo = enlace_tag['href'] if enlace_tag else ""
            enlace_completo = urllib.parse.urljoin(url, enlace_relativo) if enlace_relativo else ""

            titulo_tag: Tag | None = juego.find('h2')
            titulo = titulo_tag.get_text(strip=True) if titulo_tag else "Sin título"

            img_tag: Tag | None = juego.find('img')
            imagen_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else "Sin imagen"

            etiquetas_tags = juego.find_all('span', class_='skew-x-12')
            etiquetas = [tag.get_text(strip=True) for tag in etiquetas_tags if tag.get_text(strip=True)]

            print(f"Juego: {titulo}")
            print(f"Enlace: {enlace_completo}")
            print(f"Imagen: {imagen_url}")
            print(f"Etiquetas: {', '.join(etiquetas)}")
            print("-" * 50)
    else:
        print("Error al acceder a la página:", respuesta_pagina.status_code)


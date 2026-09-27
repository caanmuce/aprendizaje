# Calculadora de escritorio con Tkinter y MariaDB

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-2C3E50)
![MariaDB](https://img.shields.io/badge/Base%20de%20datos-MariaDB-003545?logo=mariadb&logoColor=white)
![Estado](https://img.shields.io/badge/estado-en%20desarrollo-orange)

Aplicación de escritorio desarrollada en Python que ofrece una calculadora gráfica con Tkinter y conexión opcional a MariaDB. Además de resolver operaciones matemáticas, guarda el historial de expresiones y resultados para consultarlo o limpiarlo desde la propia interfaz.

> Este repositorio reúne varios ejercicios de aprendizaje. La calculadora es el proyecto principal; las carpetas `bot/` y el archivo `practica.py` contienen experimentos independientes relacionados con agenda médica por WhatsApp y scraping web.

## Características

### Calculadora

- Interfaz gráfica de escritorio construida con Tkinter.
- Operaciones básicas: suma, resta, multiplicación y división.
- Uso de paréntesis, porcentajes, decimales y retroceso.
- Potencias mediante el botón `x²`.
- Raíces cuadradas mediante el botón `√`.
- Conversión visual de expresiones a sintaxis evaluable de Python.
- Manejo de errores durante la evaluación.
- Ventana centrada de 370 x 590 píxeles con tema oscuro y botones de color naranja.
- Historial de operaciones almacenado en MariaDB/MySQL cuando la base de datos está disponible.
- Opción para consultar y borrar el historial.
- Apertura opcional de archivos multimedia asociada a resultados concretos.

### Módulos adicionales

- `practica.py`: obtiene información de juegos desde `elenemigos.com` usando `requests` y `BeautifulSoup`.
- `bot/`: servidor Express con formulario web para agendar citas, conexión MySQL, sesión de usuario, recordatorios programados y envío de mensajes mediante WhatsApp Web.

## Tecnologías

| Área | Tecnología |
| --- | --- |
| Lenguaje principal | Python |
| Interfaz gráfica | Tkinter |
| Operaciones avanzadas | `math` y expresiones de Python |
| Persistencia | MariaDB/MySQL mediante `mysql-connector-python` |
| Scraping | `requests`, `beautifulsoup4` |
| Servidor auxiliar | Node.js, Express y `express-session` |
| Automatización auxiliar | `node-cron` y `whatsapp-web.js` |

## Estructura del proyecto

```text
.
├── calculadora.py                 # Punto de entrada de la calculadora
├── calculadora.db                 # Archivo de base de datos presente en el proyecto
├── practica.py                    # Ejercicio independiente de scraping
├── config/
│   ├── constantes.py              # Colores de la interfaz
│   └── db_config.py               # Parámetros de conexión a MariaDB
├── formulario/
│   └── form_calculadora.py        # Ventana, botones y lógica de la calculadora
├── util/
│   ├── db_manager.py              # Conexión y operaciones sobre el historial
│   └── util_ventana.py            # Utilidades de posicionamiento
├── bot/
│   ├── main.js                    # API, agenda y bot de WhatsApp
│   ├── package.json               # Dependencias del bot
│   └── public/index.html          # Panel web de login y agendamiento
└── README.md
```

## Requisitos

Para ejecutar la calculadora:

- Python 3.10 o superior.
- Tkinter instalado. En Windows normalmente viene incluido con Python.
- MariaDB o MySQL Server, solo si se desea guardar y consultar el historial.
- Base de datos `calculadora_db` creada en el servidor.

## Instalación

1. Clona el repositorio y entra en su carpeta:

   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd aprendizaje
   ```

2. Crea y activa un entorno virtual:

   ```bash
   python -m venv .venv
   ```

   En Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Instala las dependencias de Python:

   ```bash
   pip install mysql-connector-python requests beautifulsoup4
   ```

4. Crea la base de datos en MariaDB/MySQL:

   ```sql
   CREATE DATABASE calculadora_db;
   ```

5. Revisa los datos de conexión en `config/db_config.py`:

   ```python
   DB_CONFIG = {
       "host": "localhost",
       "user": "root",
       "password": "TU_CONTRASENA",
       "database": "calculadora_db",
       "port": 3306,
   }
   ```

La tabla `operaciones` se crea automáticamente al iniciar la aplicación si la conexión funciona.

## Ejecución

Desde la raíz del proyecto:

```bash
python calculadora.py
```

Si MariaDB/MySQL no está disponible, la aplicación muestra una advertencia y continúa funcionando como calculadora, pero sin las funciones de historial.

## Uso de la calculadora

1. Introduce una expresión usando los botones de la interfaz.
2. Pulsa `=` para calcular el resultado.
3. Continúa la operación usando el resultado anterior o empieza una nueva expresión.
4. Pulsa `Historial` para consultar las operaciones guardadas.
5. Usa `Limpiar Historial` para eliminar todos los registros.

Ejemplos de expresiones:

```text
12 + 8
(10 - 2) * 3
5^2
√81
```

## Módulo auxiliar: bot de citas

El subproyecto `bot/` es independiente de la calculadora. Para ejecutarlo:

```bash
cd bot
npm install
node main.js
```

Este módulo requiere una base de datos `citas_medicas` con las tablas esperadas por `main.js`. Al iniciar, muestra un código QR para vincular WhatsApp Web y levanta el panel en `http://localhost:3000`.

El servidor permite iniciar sesión, registrar pacientes y crear citas. Un proceso programado revisa las citas de las próximas 24 horas y envía recordatorios por WhatsApp.

## Seguridad y mejoras pendientes

Este proyecto tiene carácter educativo. Antes de usarlo en producción se recomienda:

- Mover contraseñas, secretos de sesión y credenciales a variables de entorno.
- No guardar contraseñas en texto plano.
- Sustituir `eval` por un analizador seguro de expresiones matemáticas.
- Validar rangos, formatos y entradas antes de guardarlas en la base de datos.
- Añadir un archivo de dependencias de Python (`requirements.txt`) y pruebas automatizadas.
- Evitar rutas absolutas para archivos multimedia y configurar esos recursos externamente.
- Añadir cierre explícito de la conexión a la base de datos al cerrar la aplicación.

## Licencia

No se ha definido una licencia para este proyecto. Añade una licencia antes de distribuirlo públicamente.
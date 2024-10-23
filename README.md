# Motor de Forecast para Red Lima

Este proyecto contiene un motor para generar, actualizar y consultar información sobre los anillos de la red de Lima. Está basado en Django y DRF (Django Rest Framework), proporcionando múltiples API endpoints para interactuar con la información de la red y los forecasts.

## Requisitos

- Python 3.x
- Django
- Django Rest Framework
- Postgres o cualquier otra base de datos compatible con Django
- Librería `coloreando` (para funciones de color en la consola)

## Instalación

1. Clona el repositorio:
    ```bash
    git clone https://github.com/tu_usuario/forecast-red-lima.git
    ```

2. Instala las dependencias del proyecto:
    ```bash
    pip install -r requirements.txt
    ```

3. Realiza las migraciones para crear las tablas en la base de datos:
    ```bash
    python manage.py migrate
    ```

4. Ejecuta el servidor:
    ```bash
    python manage.py runserver
    ```

## Funcionalidades

### 1. Estructura del motor

El motor principal está diseñado alrededor de un objeto `MotorPrincipal` que gestiona una lista de anillos (`lista_anillos_totales`).
Este objeto se actualiza mediante funciones que consultan la base de datos, y luego estructura la información en una arquitectura composite, 
utilizando los patrones `Composite`, `Enlace`, y `Agregador`.

### 2. Ejecución manual y automática

- **Ejecución manual:** Llama a `ejecutar_manualmente(fecha)` para generar la estructura de anillos para una fecha específica.
- **Ejecución automática:** Utiliza la función `ejecutar_cierto_tiempo(percentil)` para obtener la información del forecast a la fecha actual y
-  crear la estructura de los anillos.

### 3. Hilo para la ejecución periódica

Se utiliza un hilo (`ThreadAppForecast`) que ejecuta periódicamente la función `ejecutar_cierto_tiempo` cada 30 segundos.

### 4. APIs

El sistema expone varias APIs para interactuar con los datos de la red y los forecasts:

- **Consulta de información de enlaces:** `InfoView` devuelve información de los enlaces disponibles en la base de datos.
  
- **Consulta de anillos específicos:** APIs como `DataAnilloNorte1`, `DataAnilloEste`, `DataAnilloSur`, y otras permiten consultar los datos generados de diferentes anillos.

- **Top 10 enlaces con mayor tráfico:** `TopTenEnlacesMayorTrafico` retorna los 10 enlaces con mayor tráfico calculado.

- **Top 10 enlaces próximos a saturarse:** `TopTenEnlacesProximosSaturarDobleCaida` retorna los enlaces que están próximos a saturarse considerando el fallo de dos enlaces simultáneos.

- **Forecast:** 
  - **Obtener forecast:** `DataForecast` para obtener los valores almacenados de forecast.
  - **Actualizar forecast:** Enviar un archivo de forecast para actualizar los valores en la base de datos.

- **Actualización de capacidad de puerto:** `UpdateCapacidadPuerto` permite actualizar la capacidad de puerto de un enlace específico.

### 5. Estructura de datos

Los datos de los anillos y los enlaces se estructuran en un patrón composite para facilitar la adición y consulta de información. Cada anillo puede tener múltiples enlaces y agregadores asociados, y se soportan algoritmos para la simulación de caídas en los enlaces.

### 6. Manejo de fallos

El código incluye simulaciones de fallos de uno o dos enlaces, actualizando las estructuras de los anillos y generando listas de valores afectados por dichas caídas.



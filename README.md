# limpia-csv

Aplicación web sencilla para etiquetar series de tiempo en archivos CSV y calcular estadísticas básicas.

## Características

- Carga de archivos CSV desde la interfaz web.
- Etiquetado de rangos de filas con una etiqueta personalizada.
- Cálculo de estadísticas (media, mediana, promedio energético, percentiles 90 y 10) sobre los datos completos o filtrados por etiqueta.
- Interfaz basada en Flask y Bootstrap.
- Imagen Docker para una ejecución sencilla.

## Uso

1. Construir la imagen:

   ```bash
   docker build -t limpia-csv .
   ```

2. Ejecutar el contenedor:

   ```bash
   docker run -p 8080:8080 limpia-csv
   ```

3. Abrir el navegador en `http://localhost:8080` y seguir las instrucciones para subir el CSV.

El CSV debe tener la columna de tiempo en la primera posición y los datos numéricos en la segunda columna. Si no existe una columna de etiqueta, la aplicación la agregará automáticamente.

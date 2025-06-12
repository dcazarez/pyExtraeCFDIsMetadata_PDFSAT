# pyExtraeCFDIsMetadataPDFSAT

Lectura de PDF del SAT de CFDIs recibidos a CSV

En la aplicación de SAT para consultar CFDIs emitidos o recibidos, al seleccionar los CFDIS visualizados de la consulta podemos descargar a PDF la información.

Este PDF mantiene una estructura de tablas presentando 2 CFDIs por página.

Estructura del PDF: El PDF tiene cada registro de CFDI con un patrón bastante consistente. Los datos que queremos extraer son:
Folio Fiscal

RFC Emisor

Nombre o Razón Social (del emisor)

RFC Receptor

Nombre o Razón Social (del receptor)

Total

Fecha Emisión

Fecha Certificación

Estado del Comprobante

Efecto del Comprobante

PAC que Certificó

Limpieza de datos: Algunos campos pueden tener saltos de línea o espacios extra que se limpiarán en el script.

## Script

Lee el PDF en texto, crea una expresión regular para realizar el match a cada campo y convierte los valores en un CSV.

El archivo de entrada es Resultado.pdf
El archivo de salida es Resultados_CFDI.csv

### Requerimientos

1.- Crear un ambiente virtual
    -- Windows

    > pip install virtualenv
    > python -m venv env
    > env\Scripts\activate.bat 

2.- Instalar los módulos necesarios: PyPDF2 y Pandas

    > pip install -r requirements.txt

3.- Documento PDF en la ruta del entrada. Ejemplo dentro de una carpeta ./pdf y ./csv para la salida
4.- Python (ejecutado con python 3.12)
    > python '.\import PDF to CSV.py' pdf/resultados.pdf csv/out.csv

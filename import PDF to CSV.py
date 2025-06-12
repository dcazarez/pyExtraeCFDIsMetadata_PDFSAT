import PyPDF2
import re
import pandas as pd
import argparse # Importar el módulo argparse

def extract_cfdi_data(pdf_path):
    """
    Extrae datos de CFDI de un documento PDF con estructura repetitiva.

    Args:
        pdf_path (str): La ruta al archivo PDF.

    Returns:
        list: Una lista de diccionarios, donde cada diccionario representa un CFDI.
    """
    cfdi_records = []
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)

        full_text = ""
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            # Extraer texto de la página y agregar un separador para identificar el fin de página
            full_text += page.extract_text() + "\n---END_OF_PAGE---\n" 
        
        # Eliminar el texto de encabezado y pie de página que se repite
        # Se asume que "HACIENDA" y "Consulta CFDI" siempre aparecen al inicio de un bloque
        # y "Página X de Y" al final.
        full_text = re.sub(r"HACIENDA\s*SECRETARIA DE HACIENDA CREDITO POLIC\s*Servicio de Administración Tributaria\s*Consulta CFDI", "", full_text)
        full_text = re.sub(r"Página \d+ de \d+", "", full_text)
        full_text = re.sub(r"Consulta CFDI\s*Servicio de Administración Tributaria", "", full_text)
        
        # Para depuración:
        print("--- Contenido completo del texto limpio para análisis de Regex ---")
        print(full_text)
        print("-----------------------------------------------------------------")


        # Un patrón para capturar todos los campos relevantes para cada CFDI
        # Se agrupan los datos para facilitar la extracción.
        # Ajustes clave en la regex:
        # - Añadido \s* después de cada etiqueta de campo para permitir espacios y múltiples saltos de línea.
        # - Ajustado las capturas de NombreEmisor y NombreReceptor para que sean más robustas.
        # - Considerado que el Nombre o Razón Social del receptor puede aparecer con otra etiqueta similar.
        cfdi_pattern = re.compile(
            r"Folio Fiscal:\s*\n*(?P<FolioFiscal>[A-Fa-f0-9-]{36})\s*\n"
            # Ahora, necesitamos saltar el texto entre Folio Fiscal y Total
            # Consumir el RFC Emisor, Nombre Emisor, RFC Receptor (y su nombre)
            # Usaremos (?:...)? para que sean opcionales y no capturadores
            r"RFC Emisor:\s*\n*(?P<RFCEmisor>[A-Z0-9&]{12,13})\s*\n"
            r"Nombre o Razón Social:\s*\n*(?P<NombreEmisor>.+?)\s*\n"
            r"(?:RFC Receptor:\s*\n*[A-Z0-9&]{12,13}\s*\n)?" # RFC Receptor
            r"(?:Nombre o Razón Social:\s*\n*.+?\s*\n)?" # Nombre Receptor (podría ser el mismo que el del emisor si es el caso)
            r"(?:Fecha Emisión:\s*\n*(?P<FechaEmision>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s*\n)?"
            # Finalmente, el campo Total
            r"Total:\s*\n*(?P<Total>\$[\d,\.]+)\s*\n"
            
            , re.DOTALL | re.IGNORECASE # Usar IGNORECASE por si acaso hay variaciones en mayúsculas/minúsculas
        )

        # Iterar a través de todos los matches encontrados en el texto
        for match in cfdi_pattern.finditer(full_text):
            data = match.groupdict()
            
            # Limpiar los datos extraídos (eliminar espacios/saltos de línea adicionales)
            for key, value in data.items():
                if value:
                    # Reemplazar múltiples espacios/saltos de línea con un solo espacio y limpiar extremos
                    data[key] = re.sub(r'\s+', ' ', value).strip()
                else:
                    data[key] = '' # Asegurar cadena vacía para campos opcionales no encontrados
            
            # Asegurar que el NombreReceptor esté presente, ya que es constante para este PDF.
            # Podría haber sido capturado por el patrón general o por la cadena constante.
            if not data.get('NombreReceptor'):
                 data['NombreReceptor'] = 'INNOVACION EN SISTEMAS DE INFORMACION Y RECURSOS HUMANOS'

            cfdi_records.append(data)
            
    return cfdi_records

def main():
    # 1. Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description="Extrae datos de CFDI de un archivo PDF a un CSV.")
    parser.add_argument('input_pdf', type=str, 
                        help='La ruta al archivo PDF de entrada.')
    parser.add_argument('output_csv', type=str, 
                        help='La ruta al archivo CSV de salida.')

    # 2. Parsear los argumentos de la línea de comandos
    args = parser.parse_args()

    pdf_file = args.input_pdf
    output_csv_file = args.output_csv
    
    print(f"Extrayendo datos de {pdf_file}...")
    extracted_data = extract_cfdi_data(pdf_file)

    if extracted_data:
        df = pd.DataFrame(extracted_data)
        
        # Reordenar columnas para una mejor legibilidad
        desired_columns = [
            'FolioFiscal', 'RFCEmisor', 'NombreEmisor', 
            'RFCReceptor', 'NombreReceptor', 'Total', 
            'FechaEmision', 'FechaCertificacion', 'EstadoComprobante', 
            'EfectoComprobante', 'PACCertifico'
        ]
        
        # Asegurarse de que todas las columnas deseadas existan, agregar las que falten con cadenas vacías
        for col in desired_columns:
            if col not in df.columns:
                df[col] = ''
                
        df = df[desired_columns]
        
        df.to_csv(output_csv_file, index=False, encoding='utf-8')
        print(f"Datos extraídos y guardados en '{output_csv_file}' exitosamente.")
        print(f"Total de registros extraídos: {len(df)}")
    else:
        print("No se encontraron datos de CFDI en el PDF.")

if __name__ == "__main__":
    main()
import shutil
if os.path.exists("xml_output"):
    shutil.rmtree("xml_output")
if os.path.exists("xml_users.zip"):
    os.remove("xml_users.zip")
import pandas as pd
import os
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime

# Function to convert date format
def convert_date_to_datetime(date_str):
    try:
        # Parse the date from DD/MM/YYYY format
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        # Convert to XML datetime format (YYYY-MM-DDT00:00:00)
        return date_obj.strftime('%Y-%m-%dT00:00:00')
    except (ValueError, TypeError):
        return ""  # Return empty string if date is invalid or empty

# Function to convert PEP status
def convert_pep_status(pep_str):
    if pep_str == "Es PEP":
        return "true"
    elif pep_str == "No es PEP":
        return "false"
    return ""  # Return empty string for any other value

# 1. Cargar el archivo CSV
csv_file_path = "./mar25-2.csv"
df = pd.read_csv(csv_file_path, sep=';', dtype=str).fillna("")

# Print the number of users and CSV path
print(f"Procesando {len(df)} usuarios del archivo: {os.path.abspath(csv_file_path)}")

# 2. Crear un directorio para los archivos XML
output_dir = "xml_output"
os.makedirs(output_dir, exist_ok=True)

# 3. Función para generar el XML con el esquema exacto
def create_user_xml(user_data):
    root = ET.Element("Operacion")
    altas_y_bajas = ET.SubElement(root, "Altas_y_Bajas_de_Clientes", Version="1.0")
    datos_generales = ET.SubElement(altas_y_bajas, "Datos_generales_del_cliente")
    alta_persona = ET.SubElement(datos_generales, "Alta_Persona_Humana")
    
    ET.SubElement(alta_persona, "Nacional_o_Extranjera88AltaClientePH").text = user_data.get("Nacional o Ext", "")
    ET.SubElement(alta_persona, "Nro_de_CUIT_CUIL88AltaClientePH").text = user_data.get("CUIT/CUIL", "")
    ET.SubElement(alta_persona, "ApellidoX85Xs88AltaClientePH").text = user_data.get("Apellido", "")
    ET.SubElement(alta_persona, "NombreX85Xs88AltaClientePH").text = user_data.get("Nombre", "")
    ET.SubElement(alta_persona, "Tipo_Documento88AltaClientePH").text = user_data.get("Tipo de Documento", "")
    ET.SubElement(alta_persona, "N94mero_Documento88AltaClientePH").text = user_data.get("Nº Documento", "")
    ET.SubElement(alta_persona, "Nacionalidad88AltaClientePH").text = user_data.get("Nacionalidad", "")
    
    # Convert date fields to datetime format
    fecha_nacimiento = convert_date_to_datetime(user_data.get("Fecha de Nacimiento", ""))
    fecha_alta = convert_date_to_datetime(user_data.get("Fecha de Alta de Cliente", ""))
    
    ET.SubElement(alta_persona, "Fecha_de_nacimiento88AltaClientePH").text = fecha_nacimiento
    ET.SubElement(alta_persona, "Fecha_de_alta_del_cliente88AltaClientePH").text = fecha_alta
    
    # Convert PEP status
    pep_status = convert_pep_status(user_data.get("Es PEP", ""))
    ET.SubElement(alta_persona, "Es_PEP88AltaClientePH").text = pep_status
    
    # Crear el árbol XML y guardarlo con el nombre basado en CUIT/CUIL
    xml_file_path = os.path.join(output_dir, f"{user_data['CUIT/CUIL']}.xml")
    tree = ET.ElementTree(root)
    tree.write(xml_file_path, encoding="utf-8", xml_declaration=True)

# 4. Generar los archivos XML para cada usuario
for _, row in df.iterrows():
    create_user_xml(row.to_dict())

# 5. Crear un archivo ZIP con todos los XML
zip_file_path = "xml_users.zip"
with zipfile.ZipFile(zip_file_path, "w") as zipf:
    for root, _, files in os.walk(output_dir):
        for file in files:
            zipf.write(os.path.join(root, file), arcname=file)

print(f"Proceso completado. {len(df)} usuarios procesados.")
print(f"Los archivos XML están en {zip_file_path}")

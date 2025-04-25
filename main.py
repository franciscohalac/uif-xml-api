from flask import Flask, request, send_file, render_template_string
import os
import pandas as pd
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
from io import BytesIO

app = Flask(__name__)

def convert_date_to_datetime(date_str):
    try:
        return datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%dT00:00:00')
    except:
        return ""

def convert_pep_status(pep_str):
    if pep_str == "Es PEP":
        return "true"
    elif pep_str == "No es PEP":
        return "false"
    return ""

def create_user_xml(user_data, output_dir):
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
    ET.SubElement(alta_persona, "Fecha_de_nacimiento88AltaClientePH").text = convert_date_to_datetime(user_data.get("Fecha de Nacimiento", ""))
    ET.SubElement(alta_persona, "Fecha_de_alta_del_cliente88AltaClientePH").text = convert_date_to_datetime(user_data.get("Fecha de Alta de Cliente", ""))
    ET.SubElement(alta_persona, "Es_PEP88AltaClientePH").text = convert_pep_status(user_data.get("Es PEP", ""))

    xml_file_path = os.path.join(output_dir, f"{user_data['CUIT/CUIL']}.xml")
    tree = ET.ElementTree(root)
    tree.write(xml_file_path, encoding="utf-8", xml_declaration=True)

@app.route("/", methods=["GET", "POST"])
def upload_csv():
    if request.method == "POST":
        csv_file = request.files["file"]
        if not csv_file:
            return "No se subió ningún archivo."

        df = pd.read_csv(csv_file, sep=";", dtype=str).fillna("")
        
        output_dir = "xml_output"
        os.makedirs(output_dir, exist_ok=True)

        # Limpia archivos anteriores
        for f in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, f))

        # Genera XMLs
        for _, row in df.iterrows():
            create_user_xml(row.to_dict(), output_dir)

        # Crea el ZIP en memoria
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for filename in os.listdir(output_dir):
                path = os.path.join(output_dir, filename)
                zipf.write(path, arcname=filename)
        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='xml_users.zip'
        )

    # Formulario de carga
    return render_template_string('''
        <!doctype html>
        <title>Generador XML UIF</title>
        <h1>Subí tu archivo CSV</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Generar>
        </form>
    ''')

if __name__ == "__main__":
    app.run(debug=True)

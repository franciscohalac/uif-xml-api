from flask import Flask, request, send_file, render_template_string
import os
import pandas as pd
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
from io import BytesIO
import shutil

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
        file = request.files['file']
        if not file:
            return "No se subió ningún archivo", 400

        # Eliminar carpeta y ZIP anteriores
        if os.path.exists("xml_output"):
            shutil.rmtree("xml_output")
        if os.path.exists("xml_users.zip"):
            os.remove("xml_users.zip")

        os.makedirs("xml_output", exist_ok=True)

        df = pd.read_csv(file, sep=';', dtype=str).fillna("")

        for _, row in df.iterrows():
            create_user_xml(row.to_dict(), "xml_output")

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for filename in os.listdir("xml_output"):
                path = os.path.join("xml_output", filename)
                zipf.write(path, arcname=filename)
        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='xml_users.zip'
        )

    # Formulario simple
    return render_template_string('''
        <!doctype html>
        <title>Generador XML UIF</title>
        <h1>Subí tu archivo CSV con formato UIF</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file accept=".csv">
          <input type=submit value=Generar>
        </form>
    ''')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

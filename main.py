from flask import Flask, request, send_file
import subprocess

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate_xml():
    file = request.files['file']
    file.save("mar25-2.csv")

    try:
        subprocess.run(["python3", "xml-generate.py"], check=True)
        return send_file("xml_users.zip", as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

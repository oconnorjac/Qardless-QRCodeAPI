import pyodbc
import json
import os
import qrcode

from flask import Flask, request, send_file, jsonify
from flask_restful import Api
from io import BytesIO

app = Flask(__name__)
api = Api(app)

# LOCAL
# with open('secrets.json') as f:
#     secrets = json.load(f)
# connection = pyodbc.connect(secrets['DATABASE_CONNECTION_STRING'])

# HOSTED
connection = os.environ.get('DATABASE_CONNECTION_STRING')


@app.route('/', methods=['GET'])
def get():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM qr_code_data_db")
    rows = cursor.fetchall()

    qr_code_data = []
    for row in rows:
        qr_code_dic = {}
        for column in row.cursor_description:
            column_name = column[0]
            column_value = getattr(row, column_name)
            qr_code_dic[column_name] = column_value
        qr_code_data.append(qr_code_dic)

    return jsonify(qr_code_data)


@app.route('/data', methods=['POST'])
def post():
    cursor = connection.cursor()
    qr_code_data = request.get_json()

    qr_code_data_id = qr_code_data['QRCodeDataID']
    user_email = qr_code_data['UserEmail']
    cert_number = qr_code_data['CertNumber']
    scanned = qr_code_data['Scanned']
    expires = qr_code_data['Expires']
    latitude = qr_code_data['Latitude']
    longitude = qr_code_data['Longitude']

    query = """
        INSERT INTO qr_code_data_db 
            (QRCodeDataID, UserEmail, CertNumber, Scanned, Expires, Latitude, Longitude)
        VALUES 
            (?, ?, ?, ?, ?, ?, ?)
    """

    values = (qr_code_data_id, user_email, cert_number, scanned, expires, latitude, longitude)

    cursor.execute(query, values)
    connection.commit()

    return jsonify({"message": "Data added"}), 201


@app.route('/delete/<int:qr_code_data_id>', methods=['DELETE'])
def delete(qr_code_data_id):
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM qr_code_data_db WHERE QRCodeDataID = ?", qr_code_data_id)
        connection.commit()
        return jsonify({'message': 'Data deleted'}), 200
    except Exception as e:
        print(str(e))
        return jsonify({'message': 'Failed to delete data'}), 500


@app.route('/generate_qrcode', methods=['GET'])
def generate_qrcode():
    pdf_url = request.args.get('pdf_url')

    qr = qrcode.QRCode(version=7,
                       error_correction=qrcode.ERROR_CORRECT_L,
                       box_size=12,
                       border=2)
    qr.add_data(pdf_url)
    qr.make(fit=True)
    img = qr.make_image(fill='Black', back_color='White')

    img_bytes = BytesIO()
    img.save(img_bytes)
    img_bytes.seek(0)

    return send_file(img_bytes, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)

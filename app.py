import pyodbc
import qrcode
import json

from flask import Flask, request, send_file, jsonify
from flask_restful import Api
from io import BytesIO

app = Flask(__name__)
api = Api(app)

with open('secrets.json') as f:
    secrets = json.load(f)
connection = pyodbc.connect(secrets['DATABASE_CONNECTION_STRING'])


@app.route('/')
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

    cursor.close()
    connection.close()

    return jsonify(qr_code_data)


#     @marshal_with(qrCodeDataFields)
#     def post(self):
#         data = request.json
#         qr_code_data = QRCodeDataDb(userEmail=data['userEmail'],
#                                     certNum=data['certNum'],
#                                     scanned=data['scanned'],
#                                     expires=data['expires'],
#                                     latitude=data['latitude'],
#                                     longitude=data['longitude']
#                                     )
#         db.session.add(qr_code_data)
#         db.session.commit()
#         qr_code_data = QRCodeDataDb.query.all()
#         return qr_code_data
#
#     @marshal_with(qrCodeDataFields)
#     def put(self, pk):
#         data = request.json
#         qr_code_data = QRCodeDataDb.query.filter_by(qr_code_data_id=pk).first()
#         qr_code_data.certNum = data['certNum']
#         db.session.commit()
#         return QRCodeDataDb.query.all()
#
#     @marshal_with(qrCodeDataFields)
#     def delete(self, pk):
#         qr_code_data = QRCodeDataDb.query.filter_by(qr_code_data_id=pk).first()
#         db.session.delete(qr_code_data)
#         db.session.commit()
#         return
#
#
# class SingleQRCodeData(Resource):
#     @marshal_with(qrCodeDataFields)
#     def get(self, pk):
#         qr_code_data = QRCodeDataDb.query.filter_by(qr_code_data_id=pk).first()
#         return qr_code_data


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


# http://127.0.0.1:5000/generate_qrcode?pdf_url=https://qardlesspdfs.blob.core.windows.net/pdfs/MHT767-2505.pdf
# https://qardlessqrcode.azurewebsites.net/generate_qrcode?pdf_url=https://qardlesspdfs.blob.core.windows.net/pdfs/MHT767-2505.pdf

# api.add_resource(QRCodeData, '/')
# api.add_resource(SingleQRCodeData, '/')

if __name__ == '__main__':
    app.run(debug=True)

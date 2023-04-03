import base64
import qrcode

from flask import Flask, request, send_file
from flask_restful import Resource, Api, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qr_code_data.db'
db = SQLAlchemy(app)


class QRCodeDataDb(db.Model):
    qr_code_data_id = db.Column(db.Integer, primary_key=True)
    certURL = db.Column(db.String, nullable=False)
    expires = db.Column(db.String, nullable=False)

    def __repr__(self):
        return self.name


qrCodeDataFields = {
    'qr_code_data_id': fields.Integer,
    'certURL': fields.String,
    'expires': fields.String
}


class QRCodeData(Resource):
    @marshal_with(qrCodeDataFields)
    def get(self):
        qr_code_data = QRCodeDataDb.query.all()
        return qr_code_data

    @marshal_with(qrCodeDataFields)
    def post(self):
        data = request.json
        qr_code_data = QRCodeDataDb(certURL=data['certURL'], expires=data['expires'])
        db.session.add(qr_code_data)
        db.session.commit()
        qr_code_data = QRCodeDataDb.query.all()
        return qr_code_data

    @marshal_with(qrCodeDataFields)
    def put(self, pk):
        data = request.json
        qr_code_data = QRCodeDataDb.query.filter_by(qr_code_data_id=pk).first()
        qr_code_data.certURL = data['certURL']
        db.session.commit()
        return QRCodeDataDb.query.all()

    @marshal_with(qrCodeDataFields)
    def delete(self, pk):
        qr_code_data = QRCodeDataDb.query.filter_by(qr_code_data_id=pk).first()
        db.session.delete(qr_code_data)
        db.session.commit()
        return


class SingleQRCodeData(Resource):
    @marshal_with(qrCodeDataFields)
    def get(self, pk):
        qr_code_data = QRCodeDataDb.query.filter_by(qr_code_data_id=pk).first()
        return qr_code_data


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


api.add_resource(QRCodeData, '/')
api.add_resource(SingleQRCodeData, '/')

if __name__ == '__main__':
    app.run(debug=True)

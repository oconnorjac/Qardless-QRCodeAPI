from flask import Flask, request
from flask_restful import Resource, Api, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qr_code_data.db'
db = SQLAlchemy(app)


class QRCodeDataDb(db.Model):
    qr_code_data_id = db.Column(db.Integer, primary_key=True)
    certURL = db.Column(db.String, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return self.name


qrCodeDataFields = {
    'qr_code_data_id': fields.Integer,
    'certURL': fields.String,
    'expires': fields.DateTime
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


api.add_resource(QRCodeData, '/')
api.add_resource(SingleQRCodeData, '/')

if __name__ == '__main__':
    app.run(debug=True)

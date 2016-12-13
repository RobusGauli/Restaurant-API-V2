''' API Endpoints for vat, tax, service charge '''
from . import Session, app
#my own utils modules
from api.utils import SessionManager, keyrequire, lengthrequire
from api.utils import envelop, error_envelop, update_envelop, delete_envelop, post_envelop
#for debugging
import sys
#from flask 
from flask import request, url_for, redirect, jsonify
from api.models.model import  Bill, ItemOrder, Vat
#for exceptions
from sqlalchemy.exc import IntegrityError, DataError

@app.route('/api/v1/vats', methods=['POST'])
@keyrequire('name', 'value')
@lengthrequire('name', length=1)
def setVat():
	'''This function is used to store the new vat in the database
		Example : POST /api/v1/vats HTTP/1.1
		{"name" : "food", "value":34}

		Result : {
					"meta": {
					"code": 200,
					"message": "Created Successfully"
					}
					}
	'''
	with SessionManager(Session) as session:
		try:
			name = request.json['name']
			value = request.json['value']
			vat = Vat(name=name, value=value)
			session.add(vat)
			session.commit()
			return jsonify(post_envelop(200))

		except DataError: #this excepyion might probably occur if the value key has a value of non integer
			return jsonify(error_envelop(400, 'DataError', 'Use the correct value'))

		except IntegrityError:
			return jsonify(error_envelop(400, 'IntegrityError','Value : {0} already exists'.format(name)))

		except:
			return jsonify(error_envelop(400,'UnknownError','Error need to be identified'))

@app.route('/api/v1/vats', methods=['GET'])
def getVats():
	'''This function will return the all the vats available'''
	
	with SessionManager(Session) as session:
		sql_vats = session.query(Vat).order_by(Vat.id).all()
		vats = [dict(name=vat.name, value=vat.value) for vat in sql_vats]
		return jsonify(envelop(vats, 200))

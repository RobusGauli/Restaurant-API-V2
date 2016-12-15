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
from sqlalchemy.orm.exc import NoResultFound

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
	'''This function will return the all the vats available
		Example : GET /api/v1/vats HTTP/1.1
		Result : {
					"data": [
					  {
					"name": "Pizzaaa iera",
					"value": 13
					},.....
		'''
	
	with SessionManager(Session) as session:
		try:
			sql_vats = session.query(Vat).order_by(Vat.id).all()
			vats = [dict(name=vat.name, value=vat.value, id=vat.id) for vat in sql_vats]
			return jsonify(envelop(vats, 200))
		except:
			return jsonify(error_envelop(400, ' UnkownError', 'Error need to identified'))


@app.route('/api/v1/vats/<int:vat_id>', methods=['PUT'])
@lengthrequire('name')
def updateVat(vat_id):
	''' PUT /api/v1/vats/6 	HTTP/1.1
		{"name" : "New vat name", "value" : 34}

		Result : {
					"data": {
					"name": "New"
					},
					"meta": {
					"code": 200,
					"message": "Updated Successfully"
					}
				}
	'''
	with SessionManager(Session) as session:
		try:
			sql_vat = session.query(Vat).filter(Vat.id == vat_id).one()
			sql_vat.name = request.json.get('name', sql_vat.name)
			sql_vat.value = request.json.get('value', sql_vat.value)
			session.commit()
			return jsonify(update_envelop(200, data=request.json))
		except IntegrityError:
			# if name already exsits in database  
			return jsonify(error_envelop(400, 'Integrity Error','Name already Exists'))
		except:
			return jsonify(error_envelop(404, 'ValueError', 'Id not found'))
	#now the item is succesfulluy updated
	


@app.route('/api/v1/vats/<int:vat_id>', methods=['DELETE'])
def deleteVat(vat_id):
	with SessionManager(Session) as session:
		try:
			sql_vat = session.query(Vat).filter(Vat.id == vat_id).one()
			session.delete(sql_vat)
			session.commit()
			return jsonify(delete_envelop(200))
		except NoResultFound: #causes when there is no requested id in the database
			return jsonify(error_envelop(404, 'NoResultFound', 'Id : {0} Not Found'.format(vat_id)))
	#if no except is caught
	return jsonify(error_envelop(100, 'UnknownError', 'UnknownError Found'))

@app.route('/api/v1/vats/<int:vat_id>', methods=['GET'])
def getVat(vat_id):
	'''This function will return the particular vat from the list of vats
		Example : GET /api/v1/vats/1 	HTTP/1.1
		Result : {
					"id": 1,
					"uri" : "/api/v1/vats/1"
					"name": "Coke Vat",
					"value": 13
					}
	'''
	with SessionManager(Session) as session:
		try:
			sql_vat = session.query(Vat).filter(Vat.id == vat_id).one()
			name = sql_vat.name
			value = sql_vat.value
			vat_id = sql_vat.id
			uri = url_for('getVat', vat_id=vat_id)
			data = dict(name=name, value=value, id=vat_id, uri=uri)
			return jsonify(envelop(data, 200))
		except NoResultFound:
			return jsonify(error_envelop(404, 'NoResultFound', 'Id : {0} Not Found'.format(vat_id)))
	return jsonify(error_envelop(100, 'UnknownError', 'UnknownError Found'))			
''' API Endpoints for vat, tax, service charge '''
from . import Session, app
#my own utils modules
from api.utils import SessionManager, keyrequire, lengthrequire
from api.utils import envelop, error_envelop, update_envelop, delete_envelop, post_envelop
#for debugging
import sys
#from flask 
from flask import request, url_for, redirect, jsonify
from api.models.model import  Bill, ItemOrder, Vat, ServiceCharge, Membership, Payment, DineTable
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
			return jsonify(post_envelop(200, data = request.json))

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
			vats = [dict(name=vat.name, value=vat.value, id=vat.id, uri=url_for('getVat', vat_id=vat.id)) for vat in sql_vats]
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



### --------- ******Service Charge******** ------------- ####

@app.route('/api/v1/servicecharges', methods=['POST'])
@keyrequire('name', 'value')
@lengthrequire('name', length=1)
def setServiceCharge():
	'''This function is used to store the new servicecharge in the database
		Example : POST /api/v1/service charges HTTP/1.1
		{"name" : "Service Charge", "value":10}

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
			service_charge = ServiceCharge(name=name, value=value)
			session.add(service_charge)
			session.commit()
			return jsonify(post_envelop(200, data = request.json))

		except DataError: #this excepyion might probably occur if the value key has a value of non integer
			return jsonify(error_envelop(400, 'DataError', 'Use the correct value'))

		except IntegrityError:
			return jsonify(error_envelop(400, 'IntegrityError','Value : {0} already exists'.format(name)))

		except:
			return jsonify(error_envelop(400,'UnknownError','Error need to be identified'))

@app.route('/api/v1/servicecharges', methods=['GET'])
def getServiceCharges():
	'''This function will return the all the service charges available
		Example : GET /api/v1/servicecharges HTTP/1.1
		Result : {
					"data": [
					  {
					"name": "service charge",
					"value": 10
					},.....
		'''
	
	with SessionManager(Session) as session:
		try:
			sql_servicecharges = session.query(ServiceCharge).order_by(ServiceCharge.id).all()
			servicecharges = [dict(name=service.name,
								   value=service.value,
								   id=service.id,
								   uri=url_for('getServiceCharge', s_id=service.id)) for service in sql_servicecharges]
			return jsonify(envelop(servicecharges, 200))
		except:
			return jsonify(error_envelop(400, ' UnkownError', 'Error need to identified'))

@app.route('/api/v1/servicecharges/<int:s_id>', methods=['PUT'])
@lengthrequire('name')
def updateServiceCharge(s_id):
	''' PUT /api/v1/servicecharges/6 	HTTP/1.1
		{"name" : "New service name", "value" : 34}

		Result : {
					"data": {
					"name": "New service name"
					},
					"meta": {
					"code": 200,
					"message": "Updated Successfully"
					}
				}
	'''
	with SessionManager(Session) as session:
		try:
			sql_service = session.query(ServiceCharge).filter(ServiceCharge.id == s_id).one()
			sql_service.name = request.json.get('name', sql_service.name)
			sql_service.value = request.json.get('value', sql_service.value)
			session.commit()
			return jsonify(update_envelop(200, data=request.json))
		except IntegrityError:
			# if name already exsits in database  
			return jsonify(error_envelop(400, 'Integrity Error','Name already Exists'))
		except:
			return jsonify(error_envelop(404, 'ValueError', 'Id : {0} not found'.format(s_id)))
	#now the item is succesfulluy updated
	

@app.route('/api/v1/servicecharges/<int:s_id>', methods=['DELETE'])
def deleteServiceCharge(s_id):
	with SessionManager(Session) as session:
		try:
			sql_service = session.query(ServiceCharge).filter(ServiceCharge.id == s_id).one()
			session.delete(sql_service)
			session.commit()
			return jsonify(delete_envelop(200))
		except NoResultFound: #causes when there is no requested id in the database
			return jsonify(error_envelop(404, 'NoResultFound', 'Id : {0} Not Found'.format(s_id)))
	#if no except is caught
	return jsonify(error_envelop(100, 'UnknownError', 'UnknownError Found'))

@app.route('/api/v1/servicecharges/<int:s_id>', methods=['GET'])
def getServiceCharge(s_id):
	'''This function will return the particular vat from the list of vats
		Example : GET /api/v1/servicescharges/1 	HTTP/1.1
		Result : {
					"id": 1,
					"uri" : "/api/v1/servicecharges/1"
					"name": "Charges",
					"value": 10
					}
	'''
	with SessionManager(Session) as session:
		try:
			sql_service = session.query(ServiceCharge).filter(ServiceCharge.id == s_id).one()
			name = sql_service.name
			value = sql_service.value
			service_charge_id = sql_service.id
			uri = url_for('getServiceCharge', s_id=service_charge_id)
			data = dict(name=name, value=value, id=service_charge_id, uri=uri)
			return jsonify(envelop(data, 200))
		except NoResultFound:
			return jsonify(error_envelop(404, 'NoResultFound', 'Id : {0} Not Found'.format(s_id)))
	return jsonify(error_envelop(100, 'UnknownError', 'UnknownError Found'))			


##------------****PAYMENT API *****-------------##

@app.route('/api/v1/payments', methods=['POST'])
@keyrequire('p_type')
@lengthrequire('p_type', length=1)
def setPayment():
	'''This function is used to store the new payment in the database
		Example : POST /api/v1/payments HTTP/1.1
		{ "p_type": " onsite"}

		Result : {
					"meta": {
					"code": 200,
					"message": "Created Successfully"
					}
				}
	'''
	with SessionManager(Session) as session:
		try:
			
			p_type = request.json['p_type']
			payment = Payment(p_type=p_type)
			session.add(payment)
			session.commit()
			return jsonify(post_envelop(200, data = request.json))

		except DataError: #this excepyion might probably occur if the value key has a value of non integer
			return jsonify(error_envelop(400, 'DataError', 'Use the correct value'))

		except IntegrityError:
			return jsonify(error_envelop(400, 'IntegrityError','Value : {0} already exists'.format(p_type)))

		except:
			return jsonify(error_envelop(400,'UnknownError','Error need to be identified'))

@app.route('/api/v1/payments', methods=['GET'])
def getPayments():
	'''This function will return the all the payments available
		Example : GET /api/v1/payments HTTP/1.1
		Result : {
					"data": [
					  {
					"P_type": "onsite",
					
					},.....
		'''
	
	with SessionManager(Session) as session:
		try:
			sql_payments = session.query(Payment).order_by(Payment.id).all()
			payments = [dict(p_type=payment.p_type,
								   id=payment.id,
								   uri=url_for('getPayment', p_id=payment.id)
								   ) for payment in sql_payments]
			return jsonify(envelop(payments, 200))
		except:
			return jsonify(error_envelop(400, ' UnkownError', 'Error need to identified'))



@app.route('/api/v1/payments/<int:p_id>', methods=['PUT'])
@keyrequire('p_type')
@lengthrequire('p_type')
def updatePayment(p_id):
	''' PUT /api/v1/payments/6 	HTTP/1.1
		{"c_type" : "offsite"}

		Result : {
					"data": {
					"p_type": "offsite"
					},
					"meta": {
					"code": 200,
					"message": "Updated Successfully"
					}
				}
	'''
	with SessionManager(Session) as session:
		try:
			sql_payment = session.query(Payment).filter(Payment.id == p_id).one()
			sql_payment.p_type = request.json.get('p_type', sql_payment.p_type)
			session.commit()
			return jsonify(update_envelop(200, data=request.json))
		except IntegrityError:
			# if name already exsits in database  
			return jsonify(error_envelop(400, 'Integrity Error','Name already Exists'))
		except:
			return jsonify(error_envelop(404, 'ValueError', 'Id : {0} not found'.format(p_id)))
	#now the item is succesfulluy updated
	

@app.route('/api/v1/payments/<int:p_id>', methods=['DELETE'])
def deletePayment(p_id):
	with SessionManager(Session) as session:
		try:
			sql_payment = session.query(Payment).filter(Payment.id == p_id).one()
			session.delete(sql_payment)
			session.commit()
			return jsonify(delete_envelop(200))
		except NoResultFound: #causes when there is no requested id in the database
			return jsonify(error_envelop(404, 'NoResultFound', 'Id : {0} Not Found'.format(p_id)))
	#if no except is caught
	return jsonify(error_envelop(100, 'UnknownError', 'UnknownError Found'))




@app.route('/api/v1/payments/<int:p_id>', methods=['GET'])
def getPayment(p_id):
	'''This function will return the particular payment from list of payments
		Example : GET /api/v1/payments/1 	HTTP/1.1
		Result : {
					"id": 1,
					"uri" : "/api/v1/payments/1"
					"p_type": "onsite"
					}
	'''
	with SessionManager(Session) as session:
		try:
			sql_payment = session.query(Payment).filter(Payment.id == p_id).one()
			p_type = sql_payment.p_type
			id = sql_payment.id
			uri = url_for('getPayment', p_id=sql_payment.id)
			data = dict(p_type=p_type, id=id, uri=uri)
			return jsonify(envelop(data, 200))
		except NoResultFound:
			return jsonify(error_envelop(404, 'NoResultFound', 'Id : {0} Not Found'.format(p_id)))
	return jsonify(error_envelop(100, 'UnknownError', 'UnknownError Found'))			

########------DINE TABLE-------########

@app.route('/api/v1/dinetables', methods=['POST'])
@keyrequire('capacity','alias')
@lengthrequire('alias', length=1)
def setDineTable():
	'''This function is used to store the new DineTable in the database
		Example : POST /api/v1/dinetables HTTP/1.1
		{ "capicity": 4, "alias" : "Table1", "status" : "empty"}

		Result : {
					"meta": {
					"code": 200,
					"message": "Created Successfully"
					}
				}
	'''
	with SessionManager(Session) as session:
		try:
			
			capacity = request.json['capacity']
			alias = request.json['alias']
			status = request.json.get('status', 'empty')
			dine_table = DineTable(capacity=capacity, alias=alias, status=status)
			session.add(dine_table)
			session.commit()
			return jsonify(post_envelop(200, data = request.json))

		except DataError: #this excepyion might probably occur if the value key has a value of non integer
			return jsonify(error_envelop(400, 'DataError', 'Use the correct value'))

		except IntegrityError:
			return jsonify(error_envelop(400, 'IntegrityError','Value : {0} already exists'.format(alias)))

		except:
			return jsonify(error_envelop(400,'UnknownError','Error need to be identified'))


@app.route('/api/v1/dinetables', methods=['GET'])
def getDinetables():
	'''This function will return the all the payments available
		Example : GET /api/v1/dinetables HTTP/1.1
		Result : {
					"data": [
					  {
					"capacity": 2,
					"alias" : "table 1",
					"status" : "empty"
					
					},.....
		'''
	
	with SessionManager(Session) as session:
		try:
			sql_dinetables = session.query(DineTable).order_by(DineTable.id).all()
			dinetables = [dict(capacity=dinetable.capacity,
							   id=dinetable.id,
							   alias = dinetable.alias,
							   uri = url_for('getDineTable', d_id=dinetable.id)
								   ) for dinetable in sql_dinetables]
			return jsonify(envelop(dinetables, 200))
		except:
			return jsonify(error_envelop(400, ' UnkownError', 'Error need to identified'))

@app.route('/api/v1/dinetables/<int:d_id>', methods=['PUT'])
@lengthrequire('alias')
def updateDineTable(d_id):
	''' PUT /api/v1/dientables/6 	HTTP/1.1
		{"alias" : "new table name", "capacity" : 3}

		Result : {
					"data": {
					"capacity": 3,
					"alias" : "new table name"
					},
					"meta": {
					"code": 200,
					"message": "Updated Successfully"
					}
				}
	'''
	with SessionManager(Session) as session:
		try:
			sql_dinetable = session.query(DineTable).filter(DineTable.id == d_id).one()
			sql_dinetable.alias = request.json.get('alias', sql_dinetable.alias)
			sql_dinetable.capacity = request.json.get('capacity', sql_dinetable.capacity)
			session.commit()
			return jsonify(update_envelop(200, data=request.json))
		except IntegrityError:
			# if name already exsits in database  
			return jsonify(error_envelop(400, 'Integrity Error','Name already Exists'))
		except:
			return jsonify(error_envelop(404, 'ValueError', 'Id : {0} not found'.format(d_id)))
	#now the item is succesfulluy updated
	

@app.route('/api/v1/dinetables/<int:d_id>', methods=['DELETE'])
def deleteDineTable(d_id):
	with SessionManager(Session) as session:
		try:
			sql_dinetable = session.query(DineTable).filter(DineTable.id == d_id).one()
			session.delete(sql_dinetable)
			session.commit()
			return jsonify(delete_envelop(200))
		except NoResultFound: #causes when there is no requested id in the database
			return jsonify(error_envelop(404, 'NoResultFound', 'Id : {0} Not Found'.format(d_id)))
	#if no except is caught
	return jsonify(error_envelop(100, 'UnknownError', 'UnknownError Found'))

@app.route('/api/v1/dinetables/<int:d_id>', methods=['GET'])
def getDineTable(d_id):
	'''This function will return the particular payment from list of payments
		Example : GET /api/v1/dinetables/1 	HTTP/1.1
		Result : {
				"alias": "Robus",
				"capacity": 8,
				"id": 1,
				"uri" : "/api/v1/dinetables/1"
				}
	'''
	with SessionManager(Session) as session:
		try:
			sql_dinetable = session.query(DineTable).filter(DineTable.id == d_id).one()
			alias = sql_dinetable.alias
			id = sql_dinetable.id
			capacity = sql_dinetable.capacity
			uri = url_for('getDineTable', d_id=sql_dinetable.id)
			data = dict(alias=alias, capacity=capacity, id=id, uri=uri)
			return jsonify(envelop(data, 200))
		except NoResultFound:
			return jsonify(error_envelop(404, 'NoResultFound', 'Id : {0} Not Found'.format(d_id)))
	return jsonify(error_envelop(100, 'UnknownError', 'UnknownError Found'))	
''' This module is used to handle the customer endpoints'''

from . import Session, app
#my own utils modules
from api.utils import SessionManager, keyrequire, lengthrequire
from api.utils import envelop, error_envelop, update_envelop, delete_envelop, post_envelop
#for debugging
import sys
#from flask 
from flask import request, url_for, redirect, jsonify
from api.models.model import Membership, Customer
#for exceptions
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm.exc import NoResultFound

@app.route('/api/v1/memberships', methods=['POST'])
@keyrequire('m_type','discount')
@lengthrequire('m_type', length=1)
def setMembership():
	'''This function is used to store the new Membership in the database
		Example : POST /api/v1/memberships HTTP/1.1
		{ "m_type": "general", "discount" : 10, "description" : "some description"}

		Result : {
					"meta": {
					"code": 200,
					"message": "Created Successfully"
					}
				}
	'''
	with SessionManager(Session) as session:
		try:
			
			m_type = request.json['m_type']
			discount = request.json['discount']
			if not 0 <= int(discount) < 100:
				return jsonify(error_envelop(400, 'DataError', 'Enter the valid discount amount (0 to 100)'))
			description = request.json.get('description', 'No Description Available')
			membership = Membership(m_type=m_type, discount=discount, description=description)
			session.add(membership)
			session.commit()
			return jsonify(post_envelop(200, data = request.json))

		except DataError: #this excepyion might probably occur if the value key has a value of non integer
			return jsonify(error_envelop(400, 'DataError', 'Use the correct value'))

		except IntegrityError:
			return jsonify(error_envelop(400, 'IntegrityError','Value : {0} already exists'.format(m_type)))

		except:
			return jsonify(error_envelop(400,'UnknownError','Error need to be identified'))


@app.route('/api/v1/memberships', methods=['GET'])
def getMemberships():
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
			sql_memberships = session.query(Membership).order_by(Membership.id).all()
			memberships = [dict(m_type=membership.m_type,
							   id=membership.id,
							   discount = membership.discount,
							   uri = url_for('getMembership', m_id=membership.id),
							   description = membership.description
								   ) for membership in sql_memberships]
			return jsonify(envelop(memberships, 200))
		except:
			return jsonify(error_envelop(400, ' UnkownError', 'Error need to identified'))


@app.route('/api/v1/memberships/<int:m_id>', methods=['PUT'])
@lengthrequire('m_type')
def updateMembership(m_id):
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
			sql_membership = session.query(Membership).filter(Membership.id == m_id).one()
			sql_membership.m_type = request.json.get('m_type', sql_membership.m_type)
			sql_membership.discount = request.json.get('discount', sql_membership.discount)

			#check weather the discount is between 0 and 100
			if not 0 <= int(sql_membership.discount) < 100:
				return jsonify(error_envelop(400, 'DataError', 'Enter the valid discount amount (0 to 100)'))
			
			sql_membership.description = request.json.get('description', sql_membership.description)
			session.commit()
			return jsonify(update_envelop(200, data=request.json))
		except IntegrityError:
			# if name already exsits in database  
			return jsonify(error_envelop(400, 'Integrity Error','Name already Exists'))
		except NoResultFound:
			return jsonify(error_envelop(404, 'ValueError', 'Id : {0} not found'.format(m_id)))
		
	return jsonify(error_envelop(100, 'UnknownError', 'UnknownError Found'))
	#now the item is succesfulluy updated
	

@app.route('/api/v1/memberships/<int:m_id>', methods=['DELETE'])
def deleteMembership(m_id):
	with SessionManager(Session) as session:
		try:
			sql_membership = session.query(Membership).filter(Membership.id == m_id).one()
			session.delete(sql_membership)
			session.commit()
			return jsonify(delete_envelop(200))
		except NoResultFound: #causes when there is no requested id in the database
			return jsonify(error_envelop(404, 'NoResultFound', 'Id : {0} Not Found'.format(m_id)))
	#if no except is caught
	return jsonify(error_envelop(100, 'UnknownError', 'UnknownError Found'))

@app.route('/api/v1/memberships/<int:m_id>', methods=['GET'])
def getMembership(m_id):
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
			sql_membership = session.query(Membership).filter(Membership.id == m_id).one()
			m_type = sql_membership.m_type
			discount = sql_membership.discount
			description = sql_membership.description
			id = sql_membership.id
			uri = url_for('getMembership', m_id=sql_membership.id)
			data = dict(m_type=m_type, discount=discount, description=description, id=id, uri=uri)
			return jsonify(envelop(data, 200))
		except NoResultFound:
			return jsonify(error_envelop(404, 'NoResultFound', 'Id : {0} Not Found'.format(m_id)))
	return jsonify(error_envelop(100, 'UnknownError', 'UnknownError Found'))	


''' This module is used to handle the employee endpoints'''

from . import Session, app
#my own utils modules
from api.utils import SessionManager, keyrequire, lengthrequire
from api.utils import envelop, error_envelop, update_envelop, delete_envelop, post_envelop
#for debugging
import sys
#from flask 
from flask import request, url_for, redirect, jsonify
from api.models.model import EmployeePosition, Employee
#for exceptions
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm.exc import NoResultFound
#from psycopg2 import IntegrityError 

@app.route('/api/v1/employeepositions', methods = ['POST'])
@keyrequire('name')
@lengthrequire('name', length=1)
def setEmployeePosition():
	'''This method is used to store the new position for the employee
		Example : POST /api/v1/employeepostions 
		{"name" : "Cook", "description" : "THis is desription"}
	'''

	with SessionManager(Session) as session:
		try:
			name = request.json['name']
			description = request.json.get('description', 'NA')
			sql_pos = EmployeePosition(name=name, description=description)
			session.add(sql_pos)
			session.commit()
			return jsonify(post_envelop(200, data = request.json))

		except DataError: #this excepyion might probably occur if the value key has a value of non integer
			return jsonify(error_envelop(400, 'DataError', 'Use the correct value'))

		except IntegrityError:
			return jsonify(error_envelop(400, 'IntegrityError','Value : {0} already exists'.format(name)))

		except:
			return jsonify(error_envelop(400, 'UnknownError', 'Error need to be identified'))

@app.route('/api/v1/employeepositions', methods=['GET'])
def getEmployeePositions():
	'''This function will return the all the positions available
		Example : GET /api/v1/employeepositions HTTP/1.1
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
			sql_positions = session.query(EmployeePosition).order_by(EmployeePosition.id).all()
			positions = [dict(name=position.name,
							   id=position.id,
							   
							   #uri = url_for('getEmployeePosition', p_id=position.id),
							   description = position.description
								   ) for position in sql_positions]
			return jsonify(envelop(positions, 200))
		except:
			return jsonify(error_envelop(400, ' UnkownError', 'Error need to identified'))


@app.route('/api/v1/employeepositions/<int:p_id>', methods=['PUT'])
@lengthrequire('name', length=1)
def updateEmployeePosition(p_id):
	''' PUT /api/v1/dientables/6 	HTTP/1.1
		{"name" : " positions name"}

		Result : {
					"meta": {
					"code": 200,
					"message": "Updated Successfully"
					}
				}
	'''
	with SessionManager(Session) as session:
		try:
			sql_position = session.query(EmployeePosition).filter(EmployeePosition.id == p_id).one()
			sql_position.name = request.json.get('name', sql_position.name)
			sql_position.description = request.json.get('description', sql_position.description)
			session.commit()
			return jsonify(update_envelop(200, data=request.json))
		except IntegrityError:
			# if name already exsits in database  
			return jsonify(error_envelop(400, 'Integrity Error','Name already Exists'))
		except NoResultFound:
			return jsonify(error_envelop(404, 'ValueError', 'Id : {0} not found'.format(p_id)))
		
	return jsonify(error_envelop(400, 'UnknownError', 'UnknownError Found'))
	#now the item is succesfulluy updated
	

# @app.route('/api/v1/memberships/<int:m_id>', methods=['DELETE'])
# def deleteMembership(m_id):
# 	with SessionManager(Session) as session:
# 		try:
# 			sql_membership = session.query(Membership).filter(Membership.id == m_id).one()
# 			session.delete(sql_membership)
# 			session.commit()
# 			return jsonify(delete_envelop(200))
# 		except NoResultFound: #causes when there is no requested id in the database
# 			return jsonify(error_envelop(404, 'NoResultFound', 'Id : {0} Not Found'.format(m_id)))
# 	#if no except is caught
# 	return jsonify(error_envelop(100, 'UnknownError', 'UnknownError Found'))

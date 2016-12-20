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
							   
							   uri = url_for('getEmployeePosition', p_id=position.id),
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
	

@app.route('/api/v1/employeepositions/<int:p_id>', methods=['DELETE'])
def deleteEmployeePosition(p_id):
	with SessionManager(Session) as session:
		try:
			sql_position = session.query(EmployeePosition).filter(EmployeePosition.id == p_id).one()
			session.delete(sql_position)
			session.commit()
			return jsonify(delete_envelop(200))
		except NoResultFound: #causes when there is no requested id in the database
			return jsonify(error_envelop(404, 'NoResultFound', 'Id : {0} Not Found'.format(p_id)))
	#if no except is caught
	return jsonify(error_envelop(100, 'UnknownError', 'UnknownError Found'))

@app.route('/api/v1/employeepositions/<int:p_id>', methods=['GET'])
def getEmployeePosition(p_id):
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
			sql_position = session.query(EmployeePosition).filter(EmployeePosition.id == p_id).one()
			name = sql_position.name
			description = sql_position.description
			id = sql_position.id
			uri = url_for('getEmployeePosition', p_id=sql_position.id)
			data = dict(name=name, description=description, id=id, uri=uri)
			return jsonify(envelop(data, 200))
		except NoResultFound:
			return jsonify(error_envelop(404, 'NoResultFound', 'Id : {0} Not Found'.format(p_id)))
	return jsonify(error_envelop(100, 'UnknownError', 'UnknownError Found'))	

#######---------------Employeess----------#################
@app.route('/api/v1/employeepositions/<int:p_id>/employees', methods=['POST'])
@keyrequire('first_name', 'last_name', 'gender', 'date_of_birth', 'salary', 'contact_number','address')
@lengthrequire('first_name', 'last_name','address')
def setEmployeeByPosition(p_id):
	'''
	{"first_name" : "robus", "last_name" : "Gasd" , "gender" : "M", "date_of_birth" : "2014-12-12", "salary" : 2343 , "contact_number" : "25892348", "address" : "ktdm" , "age"  : 40}
	'''
	with SessionManager(Session) as session:
		try:
			first_name = request.json['first_name']
			last_name = request.json['last_name']
			gender = request.json['gender'].upper()
			middle_name = request.json.get('middle_name', 'NA')
			date_of_birth = request.json['date_of_birth']
			salary = request.json['salary']
			contact_number = request.json['contact_number']
			address = request.json['address']
			age = request.json.get('age', None)
			photo_uri = request.json.get('photo_uri', 'NA')
			email = request.json.get('email', 'NA')

			if  (not contact_number.isdigit()) or len(contact_number)>14:
				return jsonify(error_envelop(400, 'ContactError', 'Please enter the valid contact number'))
			
			if len(gender) != 1 or not ('M' in gender or 'F' in gender):
				return jsonify(error_envelop(400, 'GenderError','Please enter the valid gender. options : M or F'))
			
			if not 6 <= int(age) < 99:
				return jsonify(error_envelop(400, "Age Error", "Please enter the age between 6 and 99 "))

			
			employee = Employee(employee_position_id=p_id,
								first_name=first_name,
								middle_name=middle_name,
							    last_name=last_name, 
							    gender=gender, 
							    contact_number=contact_number, 
							    address=address, 
							    date_of_birth=date_of_birth, 
							    salary=salary, 
							    age=age, 
							    photo_uri=photo_uri, 
							    email=email)
			session.add(employee)
			session.commit()
			return jsonify(post_envelop(200, data = request.json))
		except IntegrityError:
			# if name already exsits in database  
			return jsonify(error_envelop(400, 'Integrity Error','Contact number :{0} already Exists'. format(contact_number)))
		except NoResultFound:
			return jsonify(error_envelop(404, 'ValueError', 'Id : {0} not found'.format(p_id)))
		except:
			return jsonify(error_envelop(400, 'UnkownError', 'Error not Identified'))
	return jsonify("unkown error")









@app.route('/api/v1/employeepositions/<int:p_id>/employees/<int:e_id>', methods=['PUT'])
@lengthrequire('first_name', 'last_name', 'address', 'email', length=2) #make sure the length is more than or equal to 2
def updateEmployeeByPosition(p_id, e_id):
	with SessionManager(Session) as session:
		try:
			#employee = session.query(Employee).filter(Employee.id == e_id).one()
			employee = session.query(Employee).filter(Employee.id == e_id).one()

			employee.first_name = request.json.get('first_name', employee.first_name)
			employee.middle_name = request.json.get('middle_name', employee.middle_name)
			employee.last_name = request.json.get('last_name', employee.last_name)
			employee.gender = request.json.get('gender', employee.gender)
			employee.date_of_birth = request.json.get('date_of_birth', employee.date_of_birth)
			employee.salary = request.json.get('salary', employee.salary)
			employee.contact_number = request.json.get('contact_number', employee.contact_number)
			employee.address = request.json.get('address', employee.address)
			employee.age = request.json.get('age', employee.age)
			employee.photo_uri = request.json.get('photo_uri', employee.photo_uri)
			employee.email = request.json.get('email', employee.email)

			if not 6 <= int(employee.age) < 99:
				return jsonify(error_envelop(400, "Age Error", "Please enter the age between 6 and 99 "))

			if  (not employee.contact_number.isdigit()) or len(employee.contact_number)>14:
				return jsonify(error_envelop(400, 'ContactError', 'Please enter the valid contact number'))
			
			if len(employee.gender) != 1 or not ('M' in employee.gender or 'F' in employee.gender):
				return jsonify(error_envelop(400, 'GenderError','Please enter the valid gender. options : M or F'))
			
			#id everything goes right ..make the commit
			session.commit()
			return jsonify(update_envelop(200, data=request.json))
		except IntegrityError:
			# if name already exsits in database  
			return jsonify(error_envelop(400, 'Integrity Error','Contact number :{0} already Exists'. format(contact_number)))
		except NoResultFound:
			return jsonify(error_envelop(404, 'ValueError', 'Id : {0} not found'.format(e_id)))
		except:
			return jsonify(error_envelop(400, 'UnknownError', 'Error need to be identified!!'))

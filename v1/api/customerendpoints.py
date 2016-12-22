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
#from psycopg2 import IntegrityError 

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



## ------ CUSTOMERS------ ##

@app.route('/api/v1/memberships/<int:m_id>/customers', methods=['POST'])
@keyrequire('first_name', 'last_name','gender', 'age')
@lengthrequire('first_name', 'last_name', 'address', 'email', length=2) #checking the lenght of the input fields
def setCustomersByMembership(m_id):
	'''This function is used to set the customer based on membership_id as a foriegn key'''
	
	with SessionManager(Session) as session:
		try:
			first_name = request.json['first_name']
			last_name = request.json['last_name']
			middle_name = request.json.get('middle_name', 'NA')
			contact_number = request.json.get('contact_number', 'NA')
			address = request.json.get('address', 'NA')
			gender = request.json['gender']
			age = request.json['age']
			email = request.json.get('email', 'NA')
			if not 6 <= int(age) < 99:
				return jsonify(error_envelop(400, "Age Error", "Please enter the age between 6 and 99 "))

			

			c = Customer(first_name = first_name,
						 last_name = last_name,
						 contact_number = contact_number,
						 address = address,
						 gender = gender,
						 age =age,
						 membership_id=m_id,
						 middle_name=middle_name,
						 email=email)
			session.add(c)
			session.commit()
			return jsonify(post_envelop(200, data=request.json))

		except DataError: #this excepyion might probably occur if the value key has a value of non integer
			return jsonify(error_envelop(400, 'DataError', 'Use the correct value'))

		except IntegrityError:
			return jsonify(error_envelop(400, 'IntegrityError','Violates foreign key ({0}) constraint'.format(m_id)))

		except:
			return jsonify(error_envelop(400,'UnknownError','Error need to be identified'))

@app.route('/api/v1/memberships/<int:m_id>/customers/<int:c_id>', methods=['PUT'])
@lengthrequire('first_name', 'last_name', 'address', 'email', length=2) #make sure the length is more than or equal to 2
def updateCustomerByMembership(m_id, c_id):
	with SessionManager(Session) as session:
		try:
			customer = session.query(Customer).filter(Customer.id == c_id).one()
			customer.first_name = request.json.get('first_name', customer.first_name)
			customer.middle_name = request.json.get('middle_name', customer.middle_name)
			customer.last_name = request.json.get('last_name', customer.last_name)
			customer.address = request.json.get('address', customer.address)
			customer.gender = request.json.get('gender', customer.gender)
			customer.age = request.json.get('age', customer.age)
			customer.email = request.json.get('email', customer.email)
			customer.contact_number = request.json.get('contact_number', customer.contact_number)
			try:
				customer.age = int(customer.age)
			except:
				return jsonify(error_envelop(200, "AgeError", 'Plase use the integer for age'))

			if not 7 < int(customer.age) < 99 :
				return jsonify(error_envelop(400, 'AgeError', 'Please input the valid age between 7 and 99'))
			#id everything goes right ..make the commit
			session.commit()
			return jsonify(update_envelop(200, data=request.json))
		except:
			return jsonify(error_envelop(400, 'UnknownError', 'Error need to be identified!!'))


@app.route('/api/v1/memberships/<int:m_id>/customers', methods=['GET'])
def getCustomersByMembership(m_id):
	'''A function to get the customers based on memberships'''

	with SessionManager(Session) as session:
		try:
			sql_customers = session.query(Customer).filter(Customer.membership_id == m_id).order_by(Customer.id).all()
			customers = [dict(first_name = customer.first_name,
							  middle_name = customer.middle_name,
							  last_name = customer.last_name,
							  contact_number = customer.contact_number,
							  address = customer.address,
							  gender = customer.gender,
							  age = customer.age,
							  email = customer.email,
							  id = customer.id,
							  uri = url_for('getCustomerByMembership', m_id=m_id, c_id = customer.id),
							  customer_join_date = customer.customer_join_date) for customer in sql_customers]
			return jsonify(envelop(data = customers, code=200))
			
		except:
			return jsonify(error_envelop(400, 'UnkownError', 'Somethig went wrong'))

@app.route('/api/v1/memberships/<int:m_id>/customers/<int:c_id>', methods=['DELETE'])
def deleteCustomerByMembership(m_id, c_id):

	with SessionManager(Session) as session:
		try:
			sql_customer = session.query(Customer).filter(Customer.id == c_id).one()
			session.delete(sql_customer)
			session.commit()
			return jsonify(delete_envelop(200))

		except NoResultFound: #causes when there is no requested id in the database
			return jsonify(error_envelop(404, 'NoResultFound', ' Cannot delete!!Id : {0} Not Found'.format(m_id)))

		except:
			return jsonify(error_envelop(400, 'UnknownError', 'Somethig went wrong'))

@app.route('/api/v1/memberships/<int:m_id>/customers/<int:c_id>', methods=['GET'])
def getCustomerByMembership(m_id, c_id):

	with SessionManager(Session) as session:
		try:
			sql_customer = session.query(Customer).filter(Customer.id == c_id).one()
			sql_membership = sql_customer.c_membership
			customer = dict(
							id = sql_customer.id,
							uri = url_for('getCustomerByMembership', m_id=m_id, c_id=c_id),
							first_name = sql_customer.first_name,
							middle_name = sql_customer.middle_name,
							last_name = sql_customer.last_name,
							contact_number = sql_customer.contact_number,
							gender = sql_customer.gender,
							age = sql_customer.age,
							email = sql_customer.email,
							customer_join_date = sql_customer.customer_join_date,
							address = sql_customer.address,
							membership = dict(m_type = sql_membership.m_type,
											  discount = sql_membership.discount,
											  id = sql_membership.id,
											  uri = url_for('getMembership', m_id=m_id))
							)
			return jsonify(envelop(customer, 200))

		except NoResultFound: #causes when there is no requested id in the database
			return jsonify(error_envelop(404, 'NoResultFound', ' Cannot Get!!Id : {0} Not Found'.format(c_id)))

		except:
			return jsonify(error_envelop(400, 'UnknownError', 'Something went wrong'))


#url for '/customers'
@app.route('/api/v1/customers', methods=['GET'])
def getCustomers():
	with SessionManager(Session) as session:

		sql_customers = session.query(Customer).order_by(Customer.id).all()
		customers = [dict(first_name=customer.first_name,
						  middle_name=customer.middle_name,
						  last_name=customer.last_name,
						  contact_number=customer.contact_number,
						  address=customer.address,
						  gender=customer.gender,
						  age=customer.age,
						  email=customer.email,
						  id=customer.id,
						  customer_join_date=customer.customer_join_date,
						  membership=dict(m_type=customer.c_membership.m_type, 
						  				  discount=customer.c_membership.discount,
						  				  description=customer.c_membership.description,
						  				  id=customer.c_membership.id))
					for customer in sql_customers]
		return jsonify(envelop(data=customers, code=200))
	return jsonify(error_envelop(404, 'UnknownError', 'Error need to be identified'))

@app.route('/api/v1/customers/<int:c_id>', methods=['GET'])
def getCustomer(c_id):
	with SessionManager(Session) as session:
		try:
			sql_customer = session.query(Customer).filter(Customer.id == c_id).one()
			customer=dict(first_name=sql_customer.first_name,
						  middle_name=sql_customer.middle_name,
						  last_name=sql_customer.last_name,
						  contact_number=sql_customer.contact_number,
						  address=sql_customer.address,
						  gender=sql_customer.gender,
						  age=sql_customer.age,
						  email=sql_customer.email,
						  id=sql_customer.id,
						  customer_join_date=sql_customer.customer_join_date,
						  membership=dict(m_type=sql_customer.c_membership.m_type, 
						  				  discount=sql_customer.c_membership.discount,
						  				  description=sql_customer.c_membership.description,
						  				  id=sql_customer.c_membership.id))
			return jsonify(envelop(data=customer, code=200))
		except NoResultFound:
			return jsonify(error_envelop(404, 'NoResultFound', 'Id : {0} Not Found'.format(c_id)))
	return jsonify(error_envelop(100, 'UnknownError', 'UnknownError Found'))	



	
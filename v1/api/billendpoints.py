''' This module is used to handle the employee endpoints'''

from . import Session, app
#my own utils modules
from api.utils import SessionManager, keyrequire, lengthrequire
from api.utils import envelop, error_envelop, update_envelop, delete_envelop, post_envelop
#for debugging
import sys
#from flask 
from flask import request, url_for, redirect, jsonify
from api.models.model import EmployeePosition, Employee, ItemOrder, Item, Bill, ItemCategory
#for exceptions
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm.exc import NoResultFound
#from psycopg2 import IntegrityError 

@app.route('/api/v1/bills', methods=['POST'])
@keyrequire('item_orders', 'total_price', 'on_site', 'customer_id', 'dinetable_id',\
			'employee_id', 'payment_id', 'vat_id', 'service_charge_id')
def setBill():

	with SessionManager(Session) as session:
		try:
			total_price = request.json['total_price']
			on_site = request.json.get('on_site')
			customer_id = request.json['customer_id']
			dinetable_id = request.json['dinetable_id']
			employee_id = request.json['employee_id']
			payment_id = request.json['payment_id']
			vat_id = request.json['vat_id']
			service_charge_id = request.json['service_charge_id']
			bill_description = request.json.get('bill_description', 'NA')


			item_orders = request.json['item_orders']

			if len(item_orders) < 1:
				return jsonify(error_envelop(400, 'BillError', 'Please enter atleast one item!!'))
			#if there is more than one elements in bills then create a new bill object
			bill = Bill(total_price=total_price,
						bill_description=bill_description,
						on_site=on_site,
						customer_id=customer_id,
						dinetable_id=dinetable_id,
						employee_id=employee_id,
						payment_id=payment_id,
						vat_id=vat_id,
						service_charge_id=service_charge_id)
			session.add(bill)

			for item_order in item_orders:
				item_id = item_order['item_id']
				quantity = item_order['quantity']
				order_price = item_order['order_price']
				session.add(ItemOrder(item_id=item_id,
								quantity=quantity,
								order_price=order_price,
								bill=bill))
				


			session.commit()
			return jsonify(post_envelop(200, data = request.json))

		except DataError: #this excepyion might probably occur if the value key has a value of non integer
			return jsonify(error_envelop(400, 'DataError', 'Use the correct value'))
		except IntegrityError:
			return jsonify(error_envelop(400, 'IntegrityError','Foreign Key violations. Use the correct id'))


		except:
			return jsonify(error_envelop(400, 'UnknownError', 'Error need to be identified'))




@app.route('/api/v1/bills/<int:b_id>', methods=['GET'])
def getBill(b_id):
	with SessionManager(Session) as session:
		try:
			bill = session.query(Bill).filter(Bill.id == b_id).one()
			#cus = bill.customer 
			
			customer = bill.customer.first_name if bill.customer else 'Not Available'
			dinetable = bill.dinetable.alias if bill.dinetable else 'Not Available'
			employee = bill.employee.first_name if bill.employee else 'Not Available'
			payment = bill.payment.p_type if bill.payment else 'Not Available'
			vat = bill.vat.name if bill.vat else 'Not Available'
			service_charge = bill.service_charge.name if bill.service_charge else 'Not Available' 

			bill_description = bill.bill_description
			on_site = bill.on_site
			total_price = bill.total_price
			bill_time_stamp = bill.bill_time_stamp

			items_orders = bill.items
			list_item_orders = []
			for item_order in items_orders:
				list_item_orders.append(dict(item_id = item_order.item_id,
											 bill_id = item_order.bill_id,
											 quantity = item_order.quantity,
											 order_price = item_order.order_price,
											 order_time_stamp = item_order.order_time_stamp,
											 item_name = item_order.item.name if item_order.item else 'Not Available',
											 item_unit_price = item_order.item.unit_price if item_order.item else 0.0))


			b = dict(customer=customer,
					 dinetable=dinetable,
					 employee=employee,
					 payment=payment,
					 vat=vat,
					 bill_time_stamp = str(bill_time_stamp),
					 service_charge=service_charge,
					 bill_description=bill_description,
					 on_site=on_site,
					 total_price=total_price,
					 item_orders = list_item_orders)

			return jsonify(envelop(data=b, code=200))

		except NoResultFound:
			return jsonify(error_envelop(404, 'NoResultFound', 'Id : {0} Not Found'.format(b_id)))
	return jsonify(error_envelop(400, 'UnknownError', 'Somethig went wrong'))



@app.route('/api/v1/bills', methods=['GET'])
def getBills():

	'''Get all the bills '''
	with SessionManager(Session) as session:

		sql_bills = session.query(Bill).order_by(Bill.id).all()
		bills = []
		for sql_bill in sql_bills:
			customer = sql_bill.customer.first_name if sql_bill.customer else 'Not Available'
			dinetable = sql_bill.dinetable.alias if sql_bill.dinetable else 'Not Available'
			employee = sql_bill.employee.first_name if sql_bill.employee else 'Not Available'
			payment = sql_bill.payment.p_type if sql_bill.payment else 'Not Available'
			vat = sql_bill.vat.name if sql_bill.vat else 'Not Available'
			service_charge = sql_bill.service_charge.name if sql_bill.service_charge else 'Not Available' 

			bill_description = sql_bill.bill_description
			on_site = sql_bill.on_site
			total_price = sql_bill.total_price
			bill_time_stamp = sql_bill.bill_time_stamp
			b = dict(customer=customer,
				 dinetable=dinetable,
				 employee=employee,
				 payment=payment,
				 vat=vat,
				 service_charge=service_charge,
				 bill_description=bill_description,
				 on_site=on_site,
				 total_price=total_price,
				 id = sql_bill.id,
				 bill_time_stamp = str(bill_time_stamp)
				 )
			bills.append(b)
		return jsonify(envelop(data=bills, code=200))


@app.route('/api/v1/bills/<int:b_id>', methods=['DELETE'])
def deleteBill(b_id):
	with SessionManager(Session) as session:
		try:
			bill = session.query(Bill).filter(Bill.id==b_id).one()
			session.delete(bill)
			session.commit()
			return jsonify(delete_envelop(code=200))

		except NoResultFound: #causes when there is no requested id in the database
			return jsonify(error_envelop(404, 'NoResultFound', ' Cannot delete!!Id : {0} Not Found'.format(b_id)))

	
	return jsonify(error_envelop(400, 'UnknownError', 'Somethig went wrong'))	
''' This module is used to handle the customer endpoints'''
from . import Session, app
#my own utils modules
from api.utils import SessionManager, keyrequire, lengthrequire
from api.utils import envelop, error_envelop, update_envelop, delete_envelop, post_envelop
#for debugging
import sys
#from flask 
from flask import request, url_for, redirect, jsonify
from api.models.model import Membership, Customer, Item, ItemCategory, Bill, ItemOrder
#for exceptions
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm.exc import NoResultFound
#from psycopg2 import IntegrityError 

from sqlalchemy import Column, String, Integer, ForeignKey, create_engine, Text, Enum, CheckConstraint, DateTime, func, Date, Float, desc
from sqlalchemy import DateTime, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Sequence, text
import enum

from datetime import date
@app.route('/api/v1/daily/item', methods=['GET'])
def getDailyTopItem():
	with SessionManager(Session) as session:
		result = session.execute('select sum(quantity) , item_id from itemorder where order_time_stamp::date >= current_date group by item_id order by sum(quantity) desc limit 1')
		

		
		for row in result.fetchall():
			item_id = row[1]
			total_order = row[0]
		return jsonify(item_id=item_id, total_orders=total_order)
	
@app.route('/api/v1/daily/bill', methods=['GET'])
def getDailyTotalBills():
	with SessionManager(Session) as session:
		result = session.execute('select count(id) from bills where bill_time_stamp::date = current_date limit 1')
		for row in result.fetchall():
			total_bills = row[0]
		return jsonify(total_bills=total_bills)

@app.route('/api/v1/daily/customers', methods=['GET'])
def getTotalCustomers():
	with SessionManager(Session) as session:
		result = session.execute('select count(id) from customers limit 1')
		for row in result.fetchall():
			total_customers = row[0]
		return jsonify(total_customers=total_customers)

@app.route('/api/v1/daily/dinetable', methods=['GET'])
def getTopDineTable():
	with SessionManager(Session) as session:
		result = session.execute('select dinetable_id, count(dinetable_id) from bills where bill_time_stamp::date=current_date group by dinetable_id order by count(dinetable_id) desc limit 1')
		for row in result.fetchall():
			dinetable_id = row[0]
			total_bills = row[1]
		return jsonify(dinetable_id=dinetable_id, total_bills=total_bills)


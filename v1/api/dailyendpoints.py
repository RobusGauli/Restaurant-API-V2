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
	
		
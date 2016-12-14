class SessionManager(object):
	def __init__(self, Session):
		self.Session = Session


	def __enter__(self):
		self.session = self.Session()
		return self.session

	def __exit__(self, type, value, trace):

		self.session.close()
		return 'helo there'

from functools import wraps
from flask import request
from flask import jsonify
def keyrequire(*keys):
	def decorator(func):
		@wraps(func)
		def wrap(*args, **kwargs):
			for key in keys:
				if not key in request.json:
					return jsonify(dict(error = 'missing Keys : ({0}) Please make sure keys are correct'.format(', '.join(keys))))

			return func(*args, **kwargs)
		return wrap
	return decorator

def lengthrequire(*keys, length=1):
	'''This decorator is used to check the length of the string and also make sure that the value is string and not any other type'''
	def decorator(func):
		@wraps(func)
		def wrap(*args, **kwargs):
			for key in  keys:
				value = request.json[key]
				if not isinstance(value, str) or not len(value)>=length:
					return jsonify(dict(code=400, error= 'Please make the length of the string >= {0} and value be the string'.format(length), error_type='LengthAndValueError'))
			return func(*args, **kwargs)
		return wrap
	return decorator




def envelop(data, code, pagination=None):
	'''A envelop function that decorates the json api with the dictionary with keys : code, meta, data'''

	if isinstance(pagination,str): #if pagination is str 
		response = {'meta' : dict(code=code),
					'data' : data,
					'pagination' : pagination} 
		
	else:
		response = {'meta' : dict(code=code),
					'data' : data} 
		
	return response

def error_envelop(error_code, error_type, error_message):
	response = {'meta' : dict(error_type=error_type, error_code=error_code, error_message=error_message)
	}
	return response


def update_envelop(code, data=None):
	response = {'meta' : dict(code=code, message='Updated Successfully'), 'data' : data}
	return response

def delete_envelop(code, data=None):
	response = {'meta' : dict(code=code, message='Deleted Successfully'), 'data' : data }
	return response

def post_envelop(code, data=None):
	response = {'meta' : dict(code=code, message='Created Successfully'), 'data' : data}
	return response
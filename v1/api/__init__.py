from flask import Flask 
from sqlalchemy.orm import sessionmaker
from api.models.model import init_db
#global variables
app = Flask(__name__)
#URL_DB = 'postgres://postgres:robus@localhost:5432/restaurantv2'
URL_DB = 'postgres://postgres:robus@139.59.25.134:5432/restaurantv2'
engine = init_db(URL_DB)
Session = sessionmaker(bind=engine)





from api import endpoints
from api import utilityendpoints, customerendpoints, employeeendpoints, billendpoints
from api import dailyendpoints
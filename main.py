""" Main Flask App """
import json
import urllib
import requests
from flask import Flask, session
from flask_session import Session
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from datetime import date


# Flask App initialization and Database Setting
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = '$yedMuh4mm4d13rah!m3ukhar1'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

Session(app)
db = SQLAlchemy(app)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)



# back4app data 
url = 'https://parseapi.back4app.com/classes/Carmodels_Car_Model_List?count=1&limit=10000&order=-Year'
headers = {
    'X-Parse-Application-Id': 'a6DWLKNCiKbsogNcSzd7wYO5qtct55785LfeEqzq', # This is your app's application id
    'X-Parse-REST-API-Key': '0VoZCDYVF40nmx6WrDSn9pIKHDAjeT4hyyRL46fW' # This is your app's REST API key
}



# Relational Database Tables in which each variable is a Column
class UserModel(db.Model):
    """ Table for Username and Password """
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=False)
    
    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)

class CarModel(db.Model):
    """ Table for Detail Information about a car """
    objectId = db.Column(db.String, primary_key=True)
    Year = db.Column(db.Integer, nullable=False)
    Make = db.Column(db.String, nullable=False)
    Model = db.Column(db.String, nullable=False)
    Category = db.Column(db.String, nullable=False)
    createdAt = db.Column(db.String, nullable=False)
    updatedAt = db.Column(db.String, nullable=False)


# This Creates the defined Table Schema in the database
# with app.app_context():
#     db.create_all()



# Validation Functions
def User_Pass_Validate(username, password):
    """ Function used for validation of username and password """
    
    # Here we check if the username already exists or not
    query = UserModel.query.filter_by(username=username).all()
    if (query):
        print("MESSAGE IS:  ", query)
        abort(400, message="Username already exists")
    
    # Here we define all the validation checks
    tmp = list(password)
    space = [1 if x.isspace() else 0 for x in tmp]
    num = [1 if x.isnumeric() else 0 for x in tmp]
    number_test = bool(sum(num)>0)
    length_test = bool(len(tmp)>=8 and len(username)>=8)
    alpha_space_test = bool(tmp[0].isalpha() and sum(space)==0)
    
    # Here we couple all the defined checks
    if length_test and number_test and alpha_space_test : 
        return
    elif not length_test:
        abort(400, message="Username or Password too short, must be greater or equal to 8 characters")
    elif not number_test:
        abort(400, message="Failed! Password must contain a number")
    elif not alpha_space_test:
        abort(400, message="Failed! Password must start with an alphabet and must not contain any spaces")



# Argument Parser which helps validate input
user_args = reqparse.RequestParser()
user_args.add_argument("username", type=str, help="Username is required", required=True)
user_args.add_argument("password", type=str, help="Password is required", required=True)



# Searalize an object
user_fields = {
    "username": fields.String,
    "password": fields.String
}



# Building various Api Endpoints 
class Register(Resource):
    """ This Endpoint handles Sign Up for new users """
    
    @marshal_with(user_fields)
    def post(self):
        args = user_args.parse_args()
        User_Pass_Validate(args["username"], args["password"])
        user = UserModel(username=args["username"], password=args["password"])
        user.hash_password()
        try:
            db.session.add(user)
            db.session.commit()
        except:
            abort(400, message="Error adding new user to database")
        
        return {"username":user.username}, 201


class Login(Resource):
    """ This Endpoint logs in already registered users """
    
    def post(self):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(username=args["username"]).first()
        
        if 'username' not in session:
            if user:
                pass_check = user.check_password(args["password"])
                if pass_check:
                    session["username"] = args["username"]
                    return {"message":"You are logged in"}
                else:
                    abort(400, message="Invalid username or password")
            else:
                abort(400, message="Invalid username or password")
        else:
            string_message = session["username"] + "is already logged in"
            abort(400, message=string_message)


class Logout(Resource):
    """ This Endpoint logs out an already logged in user """
    
    def get(self):
        if 'username' in session:
            session.pop('username', None)
            return {"message":"You are Logged Out"}
        else:
            abort(400, message="You are not logged in")


class StartSync(Resource):
    """ This starts the sync of the dataset """
    
    def get(self):
        Sync_dataset()
        # Sync_dataset.apply_async(countdown=86400)
        return CarModel.query.count()


class Search(Resource):
    
    def get(self, car_model, car_year):
        query = CarModel.query.filter_by(Model=car_model).filter_by(Year=car_year)
        tmp_result = []
        for cars in query:
            tmp_dic = {
                "objectId": cars.objectId,
                "Year": cars.Year,
                "Make": cars.Make,
                "Model": cars.Model,
                "Category": cars.Category,
                "createdAt": cars.createdAt,
                "updatedAt": cars.updatedAt
            }
            tmp_result.append(tmp_dic)        
        return {"result":tmp_result}, 201


# Redirecting the Endpoints to the correct URL
api.add_resource(Register, "/auth/register")
api.add_resource(Login, "/auth/login")
api.add_resource(Logout, "/auth/logout")
api.add_resource(StartSync, "/sync")
api.add_resource(Search, "/car/<string:car_model>/<int:car_year>")



# Periodic Sync of Dataset
@celery.task
def Sync_dataset():
    """ This functions collects the data from the back4app url and limits it only 10 years """
    
    data = json.loads(requests.get(url, headers=headers).content.decode('utf-8'))
    current_year = date.today().year
    car_query = CarModel.query.all()
    
    for car in data["results"]:
        # This is used if we want our Year to be equal to "cretaedAt" year
        # timestamp = list(car["createdAt"])
        # timestamp_year = timestamp[:4]
        # car_year = int(''.join(timestamp_year))
        
        car_year = car["Year"]
        
        if current_year-car_year<=10:
            car_check = True
            if car_query:
                
                for car_db in car_query:
                    if car["objectId"] == car_db.objectId:
                        car_check = False
                        break
                
            if car_check:
                car_instance = CarModel(objectId = car["objectId"], Year = car["Year"], Make = car["Make"], Model = car["Model"], Category = car["Category"], createdAt = car["createdAt"], updatedAt = car["updatedAt"] )
                try:
                    db.session.add(car_instance)
                    db.session.commit()
                    print("Car of Object ID ", car["objectId"], "has been added to the database")
                except:
                    print("Oops! Something went wrong while adding Cars to the Database")
            



# Settings for running the Flask Application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
    
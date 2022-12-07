""" Main Flask App """
from flask import Flask
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

# Flask App initialization and Database Setting
app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

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
    """ The API to handle Sign Up for new users """
    
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
        
        return user, 201

# Redirecting the Endpoints to the correct URL
api.add_resource(Register, "/auth/register")


# Settings for running the Flask Application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
    
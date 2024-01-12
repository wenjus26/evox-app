from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialisation de la base de données SQLAlchemy
db = SQLAlchemy()

# Modèle d'élément de menu
class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    url = db.Column(db.String(255))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

# Modèle de rôle
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    # Vous pouvez ajouter d'autres propriétés de rôle ici

# Table de liaison pour la relation Many-to-Many entre utilisateurs et rôles
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

# Modèle d'utilisateur
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    is_admin = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    position = db.Column(db.String(255))
    plant = db.Column(db.String(5))
    user_id = db.Column(db.String(10), unique=True)
    
    # Relation Many-to-Many avec les rôles
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')

# Modèle de Transaction
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_number = db.Column(db.String(10), unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    truck_number = db.Column(db.String(20))
    weighment_slip_number = db.Column(db.String(20), unique=True)
    gross_weight = db.Column(db.Float)
    tare = db.Column(db.Float)
    net_weight = db.Column(db.Float)
    image_path = db.Column(db.String(100))
    boquality = db.Column(db.String(100))
    balquality = db.Column(db.String(100))
    supplier_name = db.Column(db.String(255))
    lot_number = db.Column(db.String(255))
    wh_code = db.Column(db.String(255))
    commodity = db.Column(db.String(255))
    bag_type = db.Column(db.String(255))
    variety = db.Column(db.String(255))
    bag_size = db.Column(db.Float)
    sample_number = db.Column(db.String(255))
    accepted_bags = db.Column(db.Integer)
    rejected_bags = db.Column(db.Integer)
    good_bags = db.Column(db.Integer)
    damaged_bags = db.Column(db.Integer)
    moisture_humidity = db.Column(db.String(255))
    damaged_green_seed = db.Column(db.String(255))
    other_foreign_matter = db.Column(db.String(255))
    # any_other_remarks = db.Column(db.Text)

    #baltic quality
    moisture_humidity_bal = db.Column(db.String(255))
    damaged_green_seed_bal = db.Column(db.String(255))
    other_foreign_matter_bal = db.Column(db.String(255))
    any_other_remarks_bal = db.Column(db.Text)
    #end baltic
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='transactions')

# Modèle Stuffing
class Stuffing(db.Model):
    __tablename__ = 'stuffing'

    id = db.Column(db.Integer, primary_key=True)
    stuffing_number = db.Column(db.String(10), unique=True, nullable=False)
    truck_number = db.Column(db.String(255), nullable=False)
    booking_number = db.Column(db.String(10))
    container = db.Column(db.String(25),unique=True)
    forwarder = db.Column(db.String(10))
    commodity = db.Column(db.String(255))
    variety = db.Column(db.String(255))
    arrival_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    arrival_image = db.Column(db.String(100))
    
    supplier_name = db.Column(db.String(255))    
    wh_code = db.Column(db.String(255))
    bag_type = db.Column(db.String(255))
    bag_size = db.Column(db.Float)
    no_bags = db.Column(db.Integer)
    activity = db.Column(db.String(1000))
    loading_timestamp = db.Column(db.DateTime)
    controle = db.Column(db.String(1000))
    tc_status = db.Column(db.String(1000))
    seal_number = db.Column(db.String(10), unique=True)
    check_image = db.Column(db.String(100))
    seal_image = db.Column(db.String(100))
    
    lot_number = db.Column(db.String(255))
    departure_timestamp = db.Column(db.DateTime)  
    weighment_slip_number = db.Column(db.String(20), unique=True)
    gross_weight = db.Column(db.Float)
    tare = db.Column(db.Float)
    net_weight = db.Column(db.Float)
    wb_image = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='stuffings')

# Modèle de Production
class Production(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity_soya_mt = db.Column(db.Float)
    quantity_bags = db.Column(db.Integer)
    bags_size = db.Column(db.Float)
    bags_produced_per_day = db.Column(db.Integer)
    production_date = db.Column(db.Date)
    lot_number = db.Column(db.String(255))
    transaction_number = db.Column(db.String(10), db.ForeignKey('transaction.transaction_number'))
    transaction = db.relationship('Transaction', backref='production')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='productions')    

class Lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    # Ajoutez d'autres champs au besoin
    
class Agregator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    # Ajoutez d'autres champs au besoin
    lot_id = db.Column(db.Integer, db.ForeignKey('lot.id'))
    lot = db.relationship('Lot', backref='agregators')
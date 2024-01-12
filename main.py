from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import re
from datetime import datetime
import os
from sqlalchemy import or_
from flask import Flask, render_template, make_response
from io import BytesIO

#login system
 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired
from datetime import datetime
from werkzeug.security import generate_password_hash


app = Flask(__name__)
app.secret_key = "Wenjus2001?"

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'
app.config['UPLOADWB_FOLDER'] = 'static/images/transaction/weighment'  # Define the upload folder
app.config['BOQUALITY_FOLDER'] = 'static/images/transaction/boquality'  # Define the upload folder
app.config['BALQUALITY_FOLDER'] = 'static/images/transaction/balquality'  # Define the upload folder
app.config['check_FOLDER'] = 'static/images/stuffing/check'  # Define the upload folder
app.config['seal_FOLDER'] = 'static/images/stuffing/seal'  # Define the upload folder
app.config['inter_FOLDER'] = 'static/images/stuffing/interchange'  # Define the upload folder
app.config['weigh'] = 'static/images/stuffing/weighment'  # Define the upload folder
from model import db, Transaction, Stuffing, Production, Agregator, Lot

# Initialisez la base de données avec l'application Flask
db.init_app(app)# Function to generate a transaction number
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class UserForm(FlaskForm):
    first_name = StringField('Prénom', validators=[DataRequired()])
    last_name = StringField('Nom', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    position = StringField('Poste', validators=[DataRequired()])
    plant = StringField('Usine', validators=[DataRequired()])
    user_id = StringField('ID utilisateur', validators=[DataRequired()])
    is_admin = BooleanField('Administrateur')

@app.route('/user')
@login_required
def indexa():
    if current_user.is_admin:
        users = User.query.all()
    else:
        users = [current_user]
    return render_template('index.html', users=users)

@app.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        flash('Vous n\'êtes pas autorisé à créer un utilisateur.', 'danger')
        return redirect(url_for('index'))
    
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data,
            position=form.position.data,
            plant=form.plant.data,
            user_id=form.user_id.data,
            is_admin=form.is_admin.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Utilisateur créé avec succès.', 'success')
        return redirect(url_for('index'))
    return render_template('create_user.html', form=form)

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    user = User.query.get(id)
    if not user:
        flash('Utilisateur introuvable.', 'danger')
        return redirect(url_for('index'))
    if not current_user.is_admin and user != current_user:
        flash('Vous n\'êtes pas autorisé à éditer cet utilisateur.', 'danger')
        return redirect(url_for('index'))

    form = UserForm()
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.password = form.password.data
        user.position = form.position.data
        user.plant = form.plant.data
        user.user_id = form.user_id.data
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash('Utilisateur modifié avec succès.', 'success')
        return redirect(url_for('index'))
    return render_template('edit_user.html', form=form, user=user)

@app.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    user = User.query.get(id)
    if not user:
        flash('Utilisateur introuvable.', 'danger')
        return redirect(url_for('index'))
    if not current_user.is_admin and user != current_user:
        flash('Vous n\'êtes pas autorisé à supprimer cet utilisateur.', 'danger')
        return redirect(url_for('index'))

    db.session.delete(user)
    db.session.commit()
    flash('Utilisateur supprimé avec succès.', 'success')
    return redirect(url_for('index'))
@app.route('/login', methods=['GET', 'POST'])

def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        user = User.query.filter_by(user_id=user_id).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Connexion réussie', 'success')
            return redirect(url_for('index'))
        else:
            flash('Identifiant ou mot de passe incorrect', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))














#all for transaction about incomming
def generate_transaction_number(truck_number):
    def get_next_transaction_id():
        max_id = db.session.query(db.func.max(Transaction.id)).scalar()
        return max_id + 1 if max_id else 1

    next_id = get_next_transaction_id()
    alpha_part = chr(65 + (next_id - 1) // 9999)
    numeric_part = f"{(next_id - 1) % 9999 + 1:04d}"

    return f"{alpha_part}{numeric_part}-{truck_number}"

# Function to validate truck number
def validate_truck_number(truck_number):
    pattern = r'^[A-Z]{1,2}[0-9]{4}RB$'
    return re.match(pattern, truck_number) is not None

# Define the routes
@app.route('/')
def indexgeneral():
    stuffings = Stuffing.query.all()
    transactions = Transaction.query.all()


    return render_template('index.html', stuffings=stuffings, transactions=transactions)



@app.route('/transaction')
def index():
    transactions = Transaction.query.all()
    return render_template('transaction/transaction.html', transactions=transactions)

@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        truck_number = request.form['truck_number']
        weighment_slip_number = request.form['weighment_slip_number']
        gross_weight = float(request.form['gross_weight'])
        tare = float(request.form['tare'])
        net_weight = gross_weight - tare
        image = request.files['image']

        if not validate_truck_number(truck_number):
            flash("Numéro de camion invalide. Le format doit être A0000RB ou AA0000RB.", 'error')
        else:
            transaction_number = generate_transaction_number(truck_number)
            timestamp = datetime.now()

            new_transaction = Transaction(
                transaction_number=transaction_number,
                timestamp=timestamp,
                truck_number=truck_number,
                weighment_slip_number=weighment_slip_number,
                gross_weight=gross_weight,
                tare=tare,
                net_weight=net_weight,
                image_path=f'static/images/transaction/weighment{transaction_number}_wbnumber.jpg'
            )

            db.session.add(new_transaction)
            db.session.commit()

            # Save the uploaded image to the upload folder
            if image:
                image_path = os.path.join(app.config['UPLOADWB_FOLDER'], f"{transaction_number}_wbnumber.jpg")
                image.save(image_path)

            flash('Transaction ajoutée avec succès.', 'success')
            return redirect(url_for('index'))

    return render_template('transaction/add_transaction.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    transaction = Transaction.query.get(id)

    if request.method == 'POST':
        truck_number = request.form['truck_number']
        weighment_slip_number = request.form['weighment_slip_number']
        gross_weight = float(request.form['gross_weight'])
        tare = float(request.form['tare'])
        net_weight = gross_weight - tare
        image = request.files['image']

        if not validate_truck_number(truck_number):
            flash("Numéro de camion invalide. Le format doit être A0000RB ou AA0000RB.", 'error')
        else:
            transaction.truck_number = truck_number
            transaction.weighment_slip_number = weighment_slip_number
            transaction.gross_weight = gross_weight
            transaction.tare = tare
            transaction.net_weight = net_weight

            transaction.timestamp = datetime.now()

            # Save the uploaded image to the upload folder
            if image:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{transaction.transaction_number}.jpg")
                image.save(image_path)

            db.session.commit()

            flash('Transaction modifiée avec succès.', 'success')
            return redirect(url_for('index'))

    return render_template('transaction/edit_transaction.html', transaction=transaction)

@app.route('/delete/<int:id>')
def delete_transaction(id):
    transaction = Transaction.query.get(id)

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{transaction.transaction_number}.jpg")
    if os.path.exists(image_path):
        os.remove(image_path)

    db.session.delete(transaction)
    db.session.commit()

    flash('Transaction supprimée avec succès.', 'success')
    return redirect(url_for('index'))


@app.route('/transaction/<int:id>')
def view_transaction(id):
    transaction = Transaction.query.get(id)
    return render_template('transaction/view_transaction.html', transaction=transaction)


@app.route('/add_unloading_slip/<int:id>', methods=['GET', 'POST'])
def add_unloading_slip(id):
    transaction = Transaction.query.get(id)

    if request.method == 'POST':
        
        supplier_name = request.form['supplier_name']
        lot_number = request.form['lot_number']
        wh_code = request.form['wh_code']
        commodity = request.form['commodity']
        bag_type = request.form['bag_type']
        variety = request.form['variety']
        sample_number = request.form['sample_number']
        accepted_bags = int(request.form['accepted_bags'])
        rejected_bags = request.form['rejected_bags']
        if rejected_bags:
            rejected_bags = int(rejected_bags)
        else:
            rejected_bags = 0  # Ou une autre valeur par défaut si nécessaire

        
        # Récupérez les données du formulaire pour les colonnes restantes
        good_bags = request.form['good_bags']
        damaged_bags = request.form['damaged_bags']

        # Mettez à jour les colonnes restantes de la transaction
        
        transaction.supplier_name = supplier_name
        transaction.lot_number = lot_number
        transaction.wh_code = wh_code
        transaction.commodity = commodity
        transaction.bag_type = bag_type
        transaction.variety = variety
        transaction.sample_number = sample_number
        transaction.accepted_bags = accepted_bags
        transaction.rejected_bags = rejected_bags

        transaction.good_bags = good_bags
        transaction.damaged_bags = damaged_bags

        db.session.commit()

        flash('Transaction mise à jour avec succès.', 'success')

        return redirect(url_for('view_transaction', id=id))

    return render_template('transaction/add_unloading_slip.html', transaction=transaction)
import os

# ...
@app.route('/add_quality_slip/<int:id>', methods=['GET', 'POST'])
def add_quality_slip(id):
    transaction = Transaction.query.get(id)

    if request.method == 'POST':
        moisture_humidity = request.form['moisture_humidity']
        damaged_green_seed = request.form['damaged_green_seed']
        other_foreign_matter = request.form['other_foreign_matter']
        any_other_remarks = request.form['any_other_remarks']

        transaction.moisture_humidity = moisture_humidity
        transaction.damaged_green_seed = damaged_green_seed
        transaction.other_foreign_matter = other_foreign_matter
        transaction.any_other_remarks = any_other_remarks

        image = request.files['image']

        if image:
            # Combine transaction number with the filename
            filename = f"{transaction.transaction_number}_boquality.jpg"
            boquality = os.path.join(app.config['BOQUALITY_FOLDER'], filename)
            image.save(boquality)  # Utilisez image.save() au lieu de boquality.save()
            transaction.boquality = boquality

        db.session.commit()
        flash('Transaction mise à jour avec succès.', 'success')
        return redirect(url_for('view_transaction', id=id))

    return render_template('transaction/add_quality_slip.html', transaction=transaction)


#Only this for baltic control 
@app.route('/add_quality_slip_bal/<int:id>', methods=['GET', 'POST'])
def add_quality_slip_bal(id):
    transaction = Transaction.query.get(id)

    if request.method == 'POST':
        moisture_humidity_bal = request.form['moisture_humidity']
        damaged_green_seed_bal = request.form['damaged_green_seed']
        other_foreign_matter_bal = request.form['other_foreign_matter']
        any_other_remarks_bal = request.form['any_other_remarks']

        transaction.moisture_humidity_bal = moisture_humidity_bal
        transaction.damaged_green_seed_bal = damaged_green_seed_bal
        transaction.other_foreign_matter_bal = other_foreign_matter_bal
        transaction.any_other_remarks_bal = any_other_remarks_bal

        image = request.files['image']

        if image:
            # Combine transaction number with the filename
            filename = f"{transaction.transaction_number}_balquality.jpg"
            balquality = os.path.join(app.config['BALQUALITY_FOLDER'], filename)
            image.save(balquality)  # Utilisez image.save() au lieu de boquality.save()
            transaction.balquality = balquality

        db.session.commit()
        flash('Transaction mise à jour avec succès.', 'success')
        return redirect(url_for('view_transaction', id=id))

    return render_template('transaction/add_quality_slip_bal.html', transaction=transaction)




from sqlalchemy import or_

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')

    # Perform the search query on your Transaction model
    transactions = Transaction.query.filter(
        or_(
            Transaction.transaction_number.ilike(f'%{query}%'),  # Search by transaction number
            Transaction.weighment_slip_number.ilike(f'%{query}%'),  # Search by weighment slip
            Transaction.net_weight == float(query),  # Search by net weight (assuming query is a numeric value)
            Transaction.timestamp.strftime('%Y-%m-%d').ilike(f'%{query}%')  # Search by date (format: YYYY-MM-DD)
        )
    ).all()

    return render_template('transaction/search_results.html', query=query, transactions=transactions)



#STUFFING MANAGEMENT ALL CODE
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
import re
import os
from sqlalchemy import or_
from flask import Flask, render_template, make_response, Response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from weasyprint import HTML 


# Modèle de données pour le chargement (Stuffing)


@app.route('/stuffing')
def stuffing_index():
    stuffings = Stuffing.query.all()
    return render_template('stuffing/stuffing.html', stuffings=stuffings)

@app.route('/stuffing/<int:id>')
def view_stuffing(id):
    stuffing = Stuffing.query.get(id)
    return render_template('stuffing/stuffing_details.html', stuffing = stuffing)


# Route pour afficher le formulaire d'ajout d'un chargement (Stuffing)


def generate_stuffing_number(truck_number):
    def get_next_stuffing_id():
        max_id = db.session.query(db.func.max(Stuffing.id)).scalar()
        return max_id + 1 if max_id else 1

    next_id = get_next_stuffing_id()
    numeric_part = f"{(next_id - 1) % 9999 + 1:04d}"

    return f"{numeric_part}-{truck_number}"


@app.route('/stuffing/add', methods=['GET', 'POST'])
def add_stuffing():
    if request.method == 'POST':
        truck_number = request.form['truck_number']
        booking_number = request.form['booking_number']
        container = request.form['container']
        forwarder = request.form['forwarder']
        commodity = request.form['commodity']
        variety = request.form['variety']
        arrival_timestamp = datetime.now()
        image = request.files['image']
        
        if not validate_truck_number(truck_number):
            flash("Numéro de camion invalide. Le format doit être A0000RB ou AA0000RB.", 'error')
        else:
            stuffing_number = generate_stuffing_number(truck_number)

        # Créez une nouvelle instance de Stuffing
        new_stuffing = Stuffing(
            stuffing_number=stuffing_number,
            truck_number=truck_number,
            booking_number=booking_number,
            container=container,
            forwarder=forwarder,
            commodity=commodity,
            variety=variety,
            arrival_timestamp=arrival_timestamp,
            arrival_image=f'{stuffing_number}_inter.jpg'

       )

        # Ajoutez le nouveau chargement à la base de données
        db.session.add(new_stuffing)
        db.session.commit()
                    # Save theloaded image to the upload folder
        if image:
            arrival_image = os.path.join(app.config['inter_FOLDER'], f'{stuffing_number}_inter.jpg')
            image.save(arrival_image)
        
        flash('Chargement ajouté avec succès', 'success')
        return redirect(url_for('stuffing_index'))

    return render_template('stuffing/add_stuffing.html')



# Ajoutez d'autres routes et vues pour les opérations CRUD sur les chargements (Stuffing)
from datetime import datetime  # Importez le module datetime

@app.route('/stuffing/add-info/<int:id>', methods=['GET', 'POST'])
def add_stuffing_info(id):
    stuffing = Stuffing.query.get(id)
    if stuffing is None:
        flash('Transaction non trouvée', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        stuffing.supplier_name = request.form['supplier_name']
        stuffing.wh_code = request.form['wh_code']
        stuffing.bag_type = request.form['bag_type']
        stuffing.bag_size = float(request.form['bag_size'])
        stuffing.no_bags = int(request.form['no_bags'])
        stuffing.activity = request.form['activity']
        
        # Convertissez la chaîne de caractères en un objet datetime
        loading_timestamp_str = request.form['loading_timestamp']
        loading_timestamp = datetime.strptime(loading_timestamp_str, '%Y-%m-%dT%H:%M')
        
        stuffing.loading_timestamp = loading_timestamp
        
        stuffing.controle = request.form['controle']
        stuffing.tc_status = request.form['tc_status']
        stuffing.seal_number = request.form['seal_number']
        check_imag = request.files['check_image']
        if check_imag:
            # Enregistrez l'image et mettez à jour le chemin dans la base de données
            filename = f"{stuffing.stuffing_number}_check.jpg"
            check_image = os.path.join(app.config['check_FOLDER'], filename)
            check_imag.save(check_image)
            stuffing.check_image = check_image
        seal_imag = request.files['seal_image']
        if seal_imag:
            filename = f"{stuffing.stuffing_number}_seal.jpg"
            seal_image = os.path.join(app.config['seal_FOLDER'], filename)
            seal_imag.save(seal_image)
            stuffing.seal_image = seal_image
            
        db.session.commit()
        flash('Informations ajoutées à la transaction avec succès', 'success')
        return redirect(url_for('stuffing_index'))

    current_datetime = datetime.now().strftime('%Y-%m-%dT%H:%M')

    return render_template('stuffing/add_stuffing_info.html', stuffing=stuffing, current_datetime=current_datetime)

@app.route('/stuffing/add-weighment/<int:id>', methods=['GET', 'POST'])
def add_weighment_info(id):
    stuffing = Stuffing.query.get(id)
    if stuffing is None:
        flash('Transaction not found', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Parse the departure timestamp string into a datetime object
        departure_timestamp_str = request.form['departure_timestamp']
        try:
            departure_timestamp = datetime.strptime(departure_timestamp_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid departure timestamp format', 'danger')
            return redirect(url_for('/add_weighment_info', id=id))

        # Update the stuffing object with the datetime object
        stuffing.departure_timestamp = departure_timestamp
        stuffing.weighment_slip_number = request.form['weighment_slip_number']
        stuffing.gross_weight = float(request.form['gross_weight'])
        stuffing.tare = float(request.form['tare'])
        stuffing.net_weight = float(request.form['net_weight'])
        wb_imag = request.files['wb_image']

        if wb_imag:
            # Comine transaction number with the filename
            filename = f"{stuffing.stuffing_number}_wb.jpg"
            wb_image = os.path.join(app.config['weigh'], filename)
            wb_imag.save(wb_image)
            stuffing.wb_image = wb_image
        
        db.session.commit()
        flash('Weighment information added to the transaction successfully', 'success')
        return redirect(url_for('stuffing_index'))

    # Get the current date and time in the desired format ('YYYY-MM-DDTHH:MM')
    current_datetime = datetime.now().strftime('%Y-%m-%dT%H:%M')

    return render_template('stuffing/add_weighment_info.html', stuffing=stuffing, current_datetime=current_datetime)

@app.route('/edit_stuffing/<int:id>', methods=['GET', 'POST'])
def edit_stuffing(id):
    stuffing = Stuffing.query.get(id)

    if request.method == 'POST':
        stuffing_number = request.form['stuffing_number']
        truck_number = request.form['truck_number']
        booking_number = request.form['booking_number']
        container = request.form['container']
        forwarder = request.form['forwarder']
        commodity = request.form['commodity']
        variety = request.form['variety']
        arrival_timestamp = datetime.now()
        arrival_image = request.files['arrival_image']

        # Mettez à jour les attributs du chargement
        stuffing.stuffing_number = stuffing_number
        stuffing.truck_number = truck_number
        stuffing.booking_number = booking_number
        stuffing.container = container
        stuffing.forwarder = forwarder
        stuffing.commodity = commodity
        stuffing.variety = variety
        stuffing.arrival_timestamp = arrival_timestamp

        # Vérifiez si une nouvelle image d'arrivée a été téléchargée
        if arrival_image:
            # Enregistrez le nom du fichier de l'image
            stuffing.arrival_image = arrival_image.filename

        # Mettez à jour la base de données
        db.session.commit()

        flash('Chargement modifié avec succès', 'success')
        return redirect(url_for('stuffing_index'))

    return render_template('stuffing/edit_stuffing.html', stuffing=stuffing)

@app.route('/edit_supplier_info/<int:id>', methods=['GET', 'POST'])
def edit_supplier_info(id):
    stuffing = Stuffing.query.get(id)

    if request.method == 'POST':
        supplier_name = request.form['supplier_name']
        wh_code = request.form['wh_code']
        bag_type = request.form['bag_type']
        bag_size = request.form['bag_size']
        no_bags = request.form['no_bags']
        activity = request.form['activity']
        loading_timestamp_str = request.form['loading_timestamp']
        loading_timestamp = datetime.strptime(loading_timestamp_str, '%Y-%m-%dT%H:%M')
        controle = request.form['controle']
        tc_status = request.form['tc_status']
        seal_number = request.form['seal_number']
        check_image = request.files['check_image']
        seal_image = request.files['seal_image']

        # Mettez à jour les attributs du chargement
        stuffing.supplier_name = supplier_name
        stuffing.wh_code = wh_code
        stuffing.bag_type = bag_type
        stuffing.bag_size = bag_size
        stuffing.no_bags = no_bags
        stuffing.activity = activity
        stuffing.loading_timestamp = loading_timestamp
        stuffing.controle = controle
        stuffing.tc_status = tc_status
        stuffing.seal_number = seal_number

        # Vérifiez si de nouvelles images ont été téléchargées
        if check_image:
            stuffing.check_image = check_image.filename
        if seal_image:
            stuffing.seal_image = seal_image.filename

        # Mettez à jour la base de données
        db.session.commit()

        flash('Informations du Fournisseur modifiées avec succès', 'success')
        return redirect(url_for('stuffing_index'))

    return render_template('stuffing/edit_supplier_info.html', stuffing=stuffing)

@app.route('/edit_departure_info/<int:id>', methods=['GET', 'POST'])
def edit_departure_info(id):
    stuffing = Stuffing.query.get(id)

    if request.method == 'POST':
        departure_timestamp_str = request.form['departure_timestampp']
        departure_timestamp = datetime.strptime(departure_timestamp_str, '%Y-%m-%dT%H:%M')

        weighment_slip_number = request.form['weighment_slip_number']
        gross_weight = request.form['gross_weight']
        tare = request.form['tare']
        net_weight = request.form['net_weight']
        wb_image = request.files['wb_image']

        # Mettez à jour les attributs du chargement
        stuffing.departure_timestamp = departure_timestamp
        stuffing.weighment_slip_number = weighment_slip_number
        stuffing.gross_weight = gross_weight
        stuffing.tare = tare
        stuffing.net_weight = net_weight

        # Vérifiez si une nouvelle image a été téléchargée
        if wb_image:
            stuffing.wb_image = wb_image.filename

        # Mettez à jour la base de données
        db.session.commit()

        flash('Informations de Départ modifiées avec succès', 'success')
        return redirect(url_for('stuffing_index'))

    return render_template('stuffing/edit_departure_info.html', stuffing=stuffing)



@app.route('/delete_stuffing/<int:id>', methods=['GET'])
def delete_stuffing(id):
    stuffing = Stuffing.query.get(id)

    if stuffing:
        # Supprimez l'objet de la base de données
        db.session.delete(stuffing)
        db.session.commit()
        flash('Chargement supprimé avec succès', 'success')
    else:
        flash('Chargement non trouvé', 'danger')

        return redirect(url_for('stuffing_index'))


@app.route('/gene-pdf/<int:id>', methods=['GET'])
def generer_et_telecharger_pdf(id):
    transaction = Transaction.query.get(id)

    if transaction is not None:
        html_string = generer_pdf(transaction)

        pdf = HTML(string=html_string).write_pdf()

        response = Response(pdf, content_type='application/pdf')
        response.headers['Content-Disposition'] = f'inline; filename=transaction_{transaction.transaction_number}.pdf'
        return response
    else:
        return "Transaction non trouvée", 404




def generer_pdf(transaction):
    
    # Utilisez Flask pour générer l'URL absolue du logo
    logo_url = url_for('static', filename='logo2.png', _external=True)
    wb = url_for('static', filename='images/transaction/weighment/' + transaction.transaction_number + '_wbnumber.jpg',  _external=True)
    # Incluez le contenu HTML que vous avez fourni dans votre modèle HTML
    html_string = f"""
<!DOCTYPE html>
<html>

<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <title>Document PDF avec logo</title>
</head>

<body classe="A5 premier" style="font-family: Arial, sans-serif; margin: 0; padding: 0;">

    <header style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; line-height: 1.5;">
        <span>
            <h2 style="margin: 0;">BENIN ORGANICS SA</h2>
            <p style="font-size: 15px; line-height: 1.30;">Plot No P1N-17A, Glo-Djigbe Industrial Zone (GDIZ) <br>Tangbo-Djevie, Benin
            </p>
        </span>

        <img class="logo" src="{logo_url}" alt="Logo de l'entreprise" style="width: 100px; height: 100px;" >
    </header>

    <main class="nouvelle-page">
        <h3 style="font-size: 24px; text-align: center; margin: 0 auto;">QUALITY SLIP</h3>
        <div class="line" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; line-height: 1.5;">
            <span id="left">
                <strong>Supplier Name :</strong> {transaction.supplier_name}<br>
                <strong>Transaction N° :</strong> {transaction.transaction_number}<br>
                <strong>Commodity :</strong> {transaction.commodity} <br>
                <strong>Variety :</strong> {transaction.variety} <br>
                <strong>Bag Size :</strong> {transaction.bag_size}<br>
                <strong>Accepted Bags :</strong> {transaction.accepted_bags} <br>
                <strong>Rejected Bags :</strong> {transaction.rejected_bags} <br>
            </span>

            <span id="right">
                <strong>Date :</strong> {transaction.timestamp.strftime('%d %b %Y %H:%M:%S')} <br>
                <strong>Lot N° :</strong> {transaction.lot_number}<br>
                <strong>WH Code :</strong> {transaction.wh_code} <br>
                <strong>Bag Type :</strong> {transaction.bag_type} <br>
                <strong>Truck N° :</strong> {transaction.truck_number} <br>
                <strong>Sample N° :</strong> {transaction.sample_number}
            </span>
        </div>
        <br><br>
        <table style="border-collapse: collapse; width: 75%; margin-left: 0; border: 2px solid #000;">
            <tbody>
                <tr>
                    <th style="border: 1px solid #000; padding: 8px; text-align: left;">Parameter</th>
                    <th style="border: 1px solid #000; padding: 8px; text-align: center;">Measure</th>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 8px; text-align: left;">Moisture / Humidity</td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: center;"> {transaction.moisture_humidity} %</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 8px; text-align: left;">Damaged / Green Seed</td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: center;"> {transaction.damaged_green_seed} %</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 8px; text-align: left;">Other Foreign Matter (OFM)</td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: center;"> {transaction.other_foreign_matter} %</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 8px; text-align: left;">Any Other Remarks</td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: center;"> </td>
                </tr>
            </tbody>
        </table>
        <div class="line" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; line-height: 1.30;">
            <h4>Quality Checker Sign</h4> <h4>CCI / Warehouse Supervisor Sign</h4>
        </div>
        <div class="line" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; line-height: 1.30;">
            <h4>Name &amp; Stamp</h4> <h4>Name</h4>
        </div>
    </main>
</body>

</html>
<br><br><br><br><br><br<br><br><br><br><br><br><br><br><br>
<!DOCTYPE html>
<html>

<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <title>Document PDF avec logo</title>
</head>

<body classe="A5 deuxieme" style="font-family: Arial, sans-serif; margin: 0; padding: 0;">

    <header style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; line-height: 1.5;">
        <span>
            <h2 style="margin: 0;">BENIN ORGANICS SA</h2>
            <p style="font-size: 15px; line-height: 1.30;">Plot No P1N-17A, Glo-Djigbe Industrial Zone (GDIZ) <br>Tangbo-Djevie, Benin
            </p>
        </span>

        <img class="logo" src="{logo_url}" alt="Logo de l'entreprise" style="width: 100px; height: 100px;" >
    </header>

    <main class="nouvelle-page">
        <h3 style="font-size: 24px; text-align: center; margin: 0 auto;">UNLOADING SLIP</h3>
        <div class="line" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; line-height: 1.5;">
            <span id="left">
                <strong>Supplier Name :</strong> {transaction.supplier_name}<br>
                <strong>Transaction N° :</strong> {transaction.transaction_number}<br>
                <strong>Commodity :</strong> {transaction.commodity} <br>
                <strong>Variety :</strong> {transaction.variety} <br>
                <strong>Bag Size :</strong> {transaction.bag_size}<br>
                <strong>Bags Unloaded:</strong> {transaction.accepted_bags} <br>
                <strong>Bags Rejected :</strong> {transaction.rejected_bags} <br>
            </span>

            <span  id="right">
                <strong>Date :</stronG> {transaction.timestamp.strftime('%d %b %Y %H:%M')} <br>
                <strong>Activity :</strong> Unloading <br>
                <strong>Lot N° :</strong> {transaction.lot_number}<br>
                <strong>WH Code :</strong> {transaction.wh_code} <br>
                <strong>Bag Type :</strong> {transaction.bag_type}  <br>
                <strong>Truck N° :</strong> {transaction.truck_number} <br>
                <strong>Sample N° :</strong> {transaction.sample_number}
            </span>
        </div>
        <br><br>
        <div class="line" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; line-height: 1.5;">
            <table style="border-collapse: collapse; width: 75%; margin-left: 0; border: 2px solid #000;">
                <tbody>
                    <tr>
                        <th style="border: 1px solid #000; padding: 8px; text-align: left;">Sr. no.</th>
                        <th style="border: 1px solid #000; padding: 8px; text-align: center;">Bag Type-PP/JUTE</th>
                        <th style="border: 1px solid #000; padding: 8px; text-align: center;">Bags Received</th>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #000; padding: 8px; text-align: center;">1</td>
                        <td style="border: 1px solid #000; padding: 8px; text-align: center;"> {transaction.bag_type}</td>
                        <td style="border: 1px solid #000; padding: 8px; text-align: center;"> {transaction.accepted_bags} </td>
                    </tr>                    
                    <td style="border: 1px solid #000; padding: 8px; text-align: center;">2</td>
                        <td style="border: 1px solid #000; padding: 8px; text-align: center;">  </td>
                        <td style="border: 1px solid #000; padding: 8px; text-align: center;">  </td>
                    </tr>
                    <td style="border: 1px solid #000; padding: 8px; text-align: left;">Total Bags</td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: center;">  </td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: center;"> {transaction.accepted_bags} </td>
                    </tr>
    
                </tbody>
            </table>
            <span><strong>Condition of bags</strong> <br> 1. Good : {transaction.good_bags}<br> 2. Damaged : {transaction.damaged_bags} </span>
            
        </div>

        <table style="border-collapse: collapse; width: 75%; margin-left: 30%; border: 2px solid #000;">
            <tbody>
                <tr>
                    <th style="border: 1px solid #000; padding: 8px; text-align: left;">Weightment Slip N°</th>
                    <th style="border: 1px solid #000; padding: 8px; text-align: center;">Gross Weight</th>
                    <th style="border: 1px solid #000; padding: 8px; text-align: center;">Net Weight</th>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 8px; text-align: center;">{transaction.weighment_slip_number}</td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: center;"> {transaction.gross_weight}</td>
                    <td style="border: 1px solid rgb(29, 29, 203); padding: 8px; text-align: center;"> {transaction.net_weight}</td>
                </tr>                    

            </tbody>
        </table>
        <div class="line" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; line-height: 1.30;">
            <h4>Labour Contractor sign</h4> <h4>CCI / Warehouse Supervisor Sign</h4>
        </div>
        <div class="line" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; line-height: 1.30;">
            <h4>Name &amp; Stamp</h4> <h4>Name</h4>
        </div>
    </main>
</body>

</html>

<br><br><br>
</head>

<body classe="A5 deuxieme" style="font-family: Arial, sans-serif; margin: 0; padding: 0;">


    <main class="nouvelle-page">
        <img src="{wb}" style="max-width: 100%; max-height: 100%;object-fit:contain;" >
    </main>
</body>

</html>




    """

    return html_string
    








def gene_pdf(stuffing):
    # Utilisez Flask pour générer l'URL absolue du logo
    logo_url = url_for('static', filename='logo2.png', _external=True)

    # Incluez le contenu HTML en utilisant les données de l'objet Stuffing
    html_string = f"""
<!DOCTYPE html>
<html>

<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <title>Document PDF avec logo</title>
</head>

<body style="font-family: Arial, sans-serif; margin: 0; padding: 0;">

    <header style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; line-height: 1.5;">
        <span>
            <h2 style="margin: 0;">BENIN ORGANICS SA</h2>
            <p style="font-size: 15px; line-height: 1.30;">Plot No P1N-17A, Glo-Djigbe Industrial Zone (GDIZ) <br>Tangbo-Djevie, Benin
            </p>
        </span>

        <img class="logo" src="{logo_url}" alt="Logo de l'entreprise" style="width: 100px; height: 100px;" >
    </header>

    <main class="nouvelle-page">
        <h3 style="font-size: 24px; text-align: center; margin: 0 auto;">STUFFING SLIP</h3>
        <div class="line" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; line-height: 1.5;">
            <span id="left">
                <strong>Supplier Name :</strong> {stuffing.supplier_name}<br>
                <strong>Stuffing N° :</strong> {stuffing.stuffing_number}<br>
                <strong>Truck N° :</strong> {stuffing.truck_number}<br>
                <strong>Booking N° :</strong> {stuffing.booking_number} <br>
                <strong>Container N° :</strong> {stuffing.container} <br>
                <strong>Forwarder :</strong>  {stuffing.forwarder}<br>
                <strong>Commodity :</strong> {stuffing.commodity} <br>
                <strong>Variety :</strong> {stuffing.variety}  <br>
            </span>

            <span id="right">
                <strong>Arrival Date :</strong>  {stuffing.arrival_timestamp.strftime('%d %b %Y %H:%M')} <br>
                <strong>Activity :</strong>{stuffing.loading_timestamp}<br>
                <strong>Lot N° :</strong> {stuffing.lot_number}SM-BO-65 <br>
                <strong>Wh Code :</strong> {stuffing.wh_code}  <br>
                <strong>Activity :</strong> {stuffing.activity} <br>
                <strong>Bag Type :</strong> {stuffing.bag_type} <br>

            </span>
        </div>
        <br><br>
        <table style="border-collapse: collapse; width: 75%; margin-left: 0; border: 2px solid #000;">
            <tbody>
                <tr>
                    <th style="border: 1px solid #000; padding: 8px; text-align: left;">Information</th>
                    <th style="border: 1px solid #000; padding: 8px; text-align: center;">Value</th>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 8px; text-align: left;">No of Bags</td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: center;"> {stuffing.no_bags}  </td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 8px; text-align: left;">Bags Size</td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: center;">  {stuffing.bag_size}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 8px; text-align: left;">Net Weight</td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: center;">{stuffing.net_weight}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 8px; text-align: left;">Weighment Slip Number</td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: center;">{stuffing.weighment_slip_number}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 8px; text-align: left;">Controle</td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: center;"> {stuffing.controle}</td>
                </tr>
                
                <tr>
                    <td style="border: 1px solid #000; padding: 8px; text-align: left;">Seal Number</td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: center;"> {stuffing.seal_number}</td>
                </tr>
                
                <tr>
                    <td style="border: 1px solid #000; padding: 8px; text-align: left;">TC Statuc</td>
                    <td style="border: 1px solid #000; padding: 8px; text-align: center;"> {stuffing.tc_status}</td>
                </tr>

            </tbody>
        </table>
        <div class="line" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; line-height: 1.30;">
            <h4>Quality Checker Sign</h4> <h4>CCI / Warehouse Supervisor Sign</h4>
        </div>
        <div class="line" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; line-height: 1.30;">
            <h4>Name &amp; Stamp</h4> <h4>Name</h4>
        </div>
    </main>
</body>

</html>
    """
     # Configuration du papier A2 (en millimètres)
    paper_size = (594, 420)  # Largeur x Hauteur pour le format A2


    return html_string

@app.route('/generer-pdf/<int:id>', methods=['GET'])
def gene_et_telecharge_pdf(id):
    stuffing = Stuffing.query.get(id)

    if stuffing is not None:
        html_string = gene_pdf(stuffing)

        pdf = HTML(string=html_string).write_pdf()

        response = Response(pdf, content_type='application/pdf')
        response.headers['Content-Disposition'] = f'inline; filename=stuffing_{stuffing.stuffing_number}.pdf'
        return response
    else:
        return "Stuffing not found", 404


@app.route('/stuffing/details/<int:id>', methods=['GET'])
def stuffing_details(id):

    return render_template('stuffing_details.html', stuffing=stuffing_details)





















# Fonction spécifique pour les action diverses de mon application 

# Méthode pour calculer la moyenne de la colonne net_weight dans une plage de dates
def calculate_average_net_weight(start_date, end_date):
    average_net_weight = db.session.query(func.avg(Transaction.net_weight)).filter(Transaction.timestamp.between(start_date, end_date)).scalar()
    return average_net_weight


# Route pour afficher le résultat dans le template
@app.route('/average-net-weight-result/<start_date>/<end_date>', methods=['GET'])
def average_net_weight_result(start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')  # Convertir la date de début en objet datetime
    end_date = datetime.strptime(end_date, '%Y-%m-%d')      # Convertir la date de fin en objet datetime

    average_net_weight = calculate_average_net_weight(start_date, end_date)
    return render_template('average_net_weight.html', start_date=start_date, end_date=end_date, average_net_weight=average_net_weight)




######### Nettoyage de l'usine #######################################################################
@app.route('/plant-cleaning')
def plant_cleaning():
    return render_template('plant-cleaning/plant_cleaning.html')
#########################end##########################################################################

###############Production info########################################################################

@app.route('/productions')
def list_productions():
    productions = Production.query.all()
    return render_template('production/production_info.html', productions=productions)

@app.route('/production/<int:production_id>')

def production_details(production_id):
    production = Production.query.get(production_id)
    if production:
        return render_template('production_details.html', production=production)
    else:
        return "Production not found", 404
    
# Ajouter une nouvelle production
@app.route('/add-production', methods=['GET', 'POST'])
def add_production():
    if request.method == 'POST':
        # Récupérez les données du formulaire
        quantity_soya_mt = request.form['quantity_soya_mt']
        quantity_bags = request.form['quantity_bags']
        bags_size = request.form['bags_size']
        bags_produced_per_day = request.form['bags_produced_per_day']
        production_date = datetime.strptime(request.form['production_date'], '%Y-%m-%d')
        lot_number = request.form['lot_number']
        # transaction_number = request.form['transaction_number']  # S'il y a un champ de formulaire pour la transaction
        # user_id = request.form['user_id']  # S'il y a un champ de formulaire pour l'utilisateur

        # Créez une nouvelle instance de Production
        new_production = Production(
            quantity_soya_mt=quantity_soya_mt,
            quantity_bags=quantity_bags,
            bags_size=bags_size,
            bags_produced_per_day=bags_produced_per_day,
            production_date=production_date,
            lot_number=lot_number,
            # transaction_number=transaction_number,
            # user_id=user_id
        )

        # Ajoutez cette instance à la base de données
        db.session.add(new_production)
        db.session.commit()

        flash('La production a été ajoutée avec succès', 'success')
        return redirect(url_for('list_productions'))

    return render_template('production/add_production.html')

 
 
 
@app.route('/edit-production/<int:production_id>', methods=['GET', 'POST'])
def edit_production(production_id):
    production = Production.query.get(production_id)
    if not production:
        return "Production not found", 404

    if request.method == 'POST':
        production.quantity_soya_mt = request.form.get('quantity_soya_mt')
        production.quantity_bags = request.form.get('quantity_bags')
        production.bags_size = request.form.get('bags_size')
        production.bags_produced_per_day = request.form.get('bags_produced_per_day')
        production.production_date = request.form.get('production_date')
        production.lot_number = request.form.get('lot_number')

        db.session.commit()

        # Redirigez l'utilisateur vers la liste des productions ou une autre page
        return redirect('/productions')

    return render_template('edit_production.html', production=production)


@app.route('/delete-production/<int:production_id>', methods=['GET', 'POST'])
def delete_production(production_id):
    production = Production.query.get(production_id)
    if not production:
        return "Production not found", 404

    if request.method == 'POST':
        db.session.delete(production)
        db.session.commit()

        # Redirigez l'utilisateur vers la liste des productions ou une autre page
        return redirect('/productions')

    return render_template('delete_production.html', production=production)

 
####################Agregatir et lot ###########################""""""



@app.route('/agregators')
def list_agregators():
    agregators = Agregator.query.all()
    return render_template('agregator/list.html', agregators=agregators)

@app.route('/agregator/<int:agregator_id>')
def agregator_details(agregator_id):
    agregator = Agregator.query.get(agregator_id)
    return render_template('agregator/details.html', agregator=agregator)

@app.route('/add-agregator', methods=['GET', 'POST'])
def add_agregator():
    if request.method == 'POST':
        name = request.form['name']
        lot_id = request.form['lot_id']  # Sélectionnez le lot auquel associer cet agrégateur

        lot = Lot.query.get(lot_id)
        new_agregator = Agregator(name=name, lot=lot)
        db.session.add(new_agregator)
        db.session.commit()
        return redirect('/agregators')

    lots = Lot.query.all()
    return render_template('agregator/add.html', lots=lots)

@app.route('/edit-agregator/<int:agregator_id>', methods=['GET', 'POST'])
def edit_agregator(agregator_id):
    agregator = Agregator.query.get(agregator_id)
    if request.method == 'POST':
        agregator.name = request.form['name']
        lot_id = request.form['lot_id']  # Changez le lot associé si nécessaire
        lot = Lot.query.get(lot_id)
        agregator.lot = lot
        db.session.commit()
        return redirect('/agregators')

    lots = Lot.query.all()
    return render_template('agregator/edit.html', agregator=agregator, lots=lots)

@app.route('/delete-agregator/<int:agregator_id>', methods=['GET', 'POST'])
def delete_agregator(agregator_id):
    agregator = Agregator.query.get(agregator_id)
    if request.method == 'POST':
        db.session.delete(agregator)
        db.session.commit()
        return redirect('/agregators')
    return render_template('agregator/delete.html', agregator=agregator)
 
@app.route('/prediction')
def prediction():
    return render_template('prediction.html')
@app.route('/flexi')
def flexi():
    return render_template('utility/flexi.html')
@app.route('/fp')

def fp():
    return render_template('utility/fp.html')
@app.route('/chain')
def chain():
    return render_template('laboratory/chain.html')

@app.route('/hexane')
def hexadiesel():
    return render_template('hexa.html')

  
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000)

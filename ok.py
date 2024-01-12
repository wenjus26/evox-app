from flask import Flask, render_template, request, redirect, url_for, flash

from model import db, User  # Remplacez "your_app_module" par le nom de votre module principal
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = "Wenjus2001?"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'

def create_admin():
    admin_username = 'RejusteW26'
    admin_first_name = 'Rejuste'
    admin_last_name = 'WENOUMI'
    admin_email = 'rejustewenoumi@gmail.com'
    admin_password = 'Wenjus2001?'  # Assurez-vous de changer le mot de passe selon vos besoins
    admin_position = 'MIS Executive'
    admin_plant = 'SOYA Plant'
    admin_user_id = 'RejusteW26'
    
    # Vérifiez si l'administrateur existe déjà
    existing_admin = User.query.filter_by(username=admin_username, is_admin=True).first()
    if existing_admin:
        print(f"L'administrateur avec le nom d'utilisateur '{admin_username}' existe déjà.")
    else:
        # Créez un nouvel administrateur avec les données fournies
        password_hash = generate_password_hash(admin_password, method='sha256')
        admin = User(
            username=admin_username,
            first_name=admin_first_name,
            last_name=admin_last_name,
            email=admin_email,
            password=password_hash,
            position=admin_position,
            plant=admin_plant,
            user_id=admin_user_id,
            is_admin=True
        )
        
        # Ajoutez l'administrateur à la base de données
        db.session.add(admin)
        db.session.commit()
        print(f"Administrateur '{admin_username}' inséré avec succès.")

if __name__ == '__main__':
    with app.app_context():
        create_admin()












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







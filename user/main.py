from sre_constants import SUCCESS
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


# Table de jointure User-Roles
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)


# Modèle pour les rôles
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# Modèle pour les utilisateurs
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))


#La gestion des roles utilisateurs pour le system
from functools import wraps
from flask import flash, redirect, url_for, session


# Fonction pour vérifier si l'utilisateur a le rôle requis
def role_required(role_name):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            # Vérifiez si toutes les informations de l'utilisateur sont dans la session
            if 'user_id' in session:
                user_id = session['user_id']
                user = User.query.get(user_id)
                if user:
                    user_roles = [role.name for role in user.roles]
                    if role_name in user_roles:
                        return func(*args, **kwargs)
            flash("Vous n'avez pas l'autorisation requise pour accéder à cette page.", 'error')
            # Ajoutez le message flash à la session
            session['error_message'] = "Vous n'avez pas l'autorisation requise pour accéder à cette page."
            # Rediriger l'utilisateur vers la même page
            return redirect(request.referrer or url_for('home'))
        return decorated_function
    return decorator
#--------------------------------------------------------------------------------------------------#
# Gestion des permissions sur cette plateformes
# Route pour assigner un rôle à un utilisateur
@app.route('/users/assign_role/<int:user_id>', methods=['GET', 'POST'])
@role_required('admin')
def assign_role(user_id):
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()
    if request.method == 'POST':
        selected_roles = request.form.getlist('roles')
        user.roles = Role.query.filter(Role.id.in_(selected_roles)).all()
        db.session.commit()
        flash('Roles assigned successfully!','success')
        return redirect(url_for('list_users'))
    return render_template('roles/assign_role.html', user=user, roles=roles)

# Route pour modifier les rôles d'un utilisateur
@app.route('/users/edit_roles/<int:user_id>', methods=['GET', 'POST'])
def edit_roles(user_id):
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()
    if request.method == 'POST':
        selected_roles = request.form.getlist('roles')
        user.roles = Role.query.filter(Role.id.in_(selected_roles)).all()
        db.session.commit()
        flash('User roles updated successfully!', 'success')
        return redirect(url_for('list_users'))
    return render_template('edit_user_roles.html', user=user, roles=roles)

@app.route('/users/remove_role/<int:user_id>', methods=['GET', 'POST'])
def remove_role(user_id):
    if request.method == 'POST':
        user = User.query.get_or_404(user_id)
        selected_roles = request.form.getlist('roles')
        user.roles = [role for role in user.roles if str(role.id) not in selected_roles]
        db.session.commit()
        flash('Role removed successfully!','success')
        return redirect(url_for('list_users'))
    else:
        # Gérer les requêtes GET
        user = User.query.get_or_404(user_id)
        return render_template('roles/remove_role.html', user=user)

#-------------------------------------------------------------------------------------------------------------#
#Mise en place de crud pour les roles des utilisateurs

# Route for listing all roles
@app.route('/roles')

def list_roles():
    roles = Role.query.all()
    return render_template('roles/list_roles.html', roles=roles)

# Route for adding a new role
@app.route('/roles/add', methods=['GET', 'POST'])

def add_role():
    if request.method == 'POST':
        name = request.form['name']
        new_role = Role(name=name)
        db.session.add(new_role)
        db.session.commit()
        flash('Role added successfully!','success')
        return redirect(url_for('list_roles'))
    return render_template('roles/add_role.html')

# Route for updating an existing role
@app.route('/roles/edit/<int:id>', methods=['GET', 'POST'])
@role_required('DELETE')
def edit_role(id):
    role = Role.query.get_or_404(id)
    if request.method == 'POST':
        role.name = request.form['name']
        db.session.commit()
        flash('Role updated successfully!','success')
        return redirect(url_for('list_roles'))
    return render_template('roles/edit_role.html', role=role)

# Route for deleting an existing role
@app.route('/roles/delete/<int:id>', methods=['POST'])

def delete_role(id):
    role = Role.query.get_or_404(id)
    db.session.delete(role)
    db.session.commit()
    flash('Role deleted successfully!')
    return redirect(url_for('list_roles'))

#-------------------------------------------------------------------------------------------------------------#
# Route for home page
# Route pour la page d'accueil
 
@app.route('/home')
def home():
    # Vérifie si l'utilisateur est connecté
    if 'username' in session:
        # Récupère l'utilisateur connecté à partir de la session
        username = session['username']
        user = User.query.filter_by(username=username).first()
        
        # Vérifie si l'utilisateur existe dans la base de données
        if user:
            # Récupère tous les rôles de l'utilisateur
            roles = [role.name for role in user.roles]
            
            # Renvoie la page d'accueil avec les rôles de l'utilisateur
            return render_template('home.html', username=username, roles=roles)
    
    # Redirige vers la page de connexion si l'utilisateur n'est pas connecté ou n'existe pas
    return redirect(url_for('login'))



# Route pour la page d'index
@app.route('/')
def index():
    return redirect(url_for('home'))

# Route pour l'inscription de l'utilisateur
@app.route('/register', methods=['GET', 'POST'])

def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # Vérifie si l'utilisateur existe déjà
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!','error')
        else:
            # Crée un nouvel utilisateur
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!','success')
            return redirect(url_for('login'))
    return render_template('authentification/register.html')

# Route pour la connexion de l'utilisateur
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Vérifie si l'utilisateur existe et que le mot de passe est correct
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            session['user_id'] = user.id
            flash('Login successful!','success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!','error')
    return render_template('authentification/login.html')

# Route pour changer de mot de passe
@app.route('/change_password', methods=['GET', 'POST'])

def change_password():
    if request.method == 'POST':
        username = request.form['username']
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        # Vérifie si l'utilisateur existe et que l'ancien mot de passe est correct
        user = User.query.filter_by(username=username, password=old_password).first()
        if user:
            user.password = new_password
            db.session.commit()
            flash('Password changed successfully!','success')
            return redirect(url_for('login'))
        else:
            flash('Incorrect username or old password!','error')
    return render_template('authentification/change_password.html')

# Route pour la déconnexion de l'utilisateur
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out successfully!','success')
    return redirect(url_for('login'))


# Route pour afficher la liste des utilisateurs
@app.route('/users')
def list_users():
    users = User.query.all()
    return render_template('user/list_users.html', users=users)

# Route pour ajouter un nouvel utilisateur
@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully!','success')
        return redirect(url_for('list_users'))
    return render_template('add_user.html')

# Route pour éditer les informations d'un utilisateur
@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.password = request.form['password']
        db.session.commit()
        flash('User updated successfully!','success')
        return redirect(url_for('list_users'))
    return render_template('edit_user.html', user=user)

# Route pour supprimer un utilisateur
@app.route('/users/delete/<int:id>', methods=['POST'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!','success')
    return redirect(url_for('list_users'))








# Route pour le tableau de bord logistique
@app.route('/logistics/dashboard')
@role_required('logistique')
def logistics_dashboard():
    return render_template('logistics_dashboard.html')

# Route pour l'inventaire du entrepôt
@app.route('/warehouse/inventory')
@role_required('warehouse')
def warehouse_inventory():
    return render_template('warehouse_inventory.html')

if __name__ == '__main__':
    # Create the database tables
    with app.app_context():
        db.create_all()
    app.run(debug=True)

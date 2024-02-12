from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Wenjus2001?'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration de l'extension Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'rejustewenoumi@gmail.com'
app.config['MAIL_PASSWORD'] = 'Wenjus2001?'

db = SQLAlchemy(app)
mail = Mail(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    email_confirmed = db.Column(db.Boolean, default=False)

# Route pour l'inscription d'un utilisateur
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
        
        # Envoi de l'email de confirmation
        token = secrets.token_hex(16)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        msg = Message('Confirm Email', sender='rejustewenoumi@gmail.com', recipients=[email])
        msg.body = f'To confirm your email, visit the following link: {confirm_url}'
        mail.send(msg)

        flash('Please check your email to confirm your account.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Route pour confirmer l'email
@app.route('/confirm_email/<token>')
def confirm_email(token):
    user = User.query.filter_by(email_token=token).first_or_404()
    user.email_confirmed = True
    db.session.commit()
    flash('Your email has been confirmed! You can now login.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Create the database tables
    with app.app_context():
        db.create_all()
    app.run(debug=True , port=5005)

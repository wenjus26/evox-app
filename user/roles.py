from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///roles.db'
db = SQLAlchemy(app)



if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from pathlib import Path

game = Flask(__name__)
game.secret_key = 'asdasda'
game.config['SQLALCHEMY_DATABASE_URI']='sqlite:///game.db'
db = SQLAlchemy(game)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(game)
login_manager.login_message = '''It seems like you don\'t have permissions to view this page. 
Try again or create an account.'''

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return Users.query.get(int(user_id))

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    characters_list = db.Column(db.Text, default='')

    def __repr__(self):
        return self.username

class Characters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_name = db.Column(db.String(50), nullable = False)
    owned_by_user = db.Column(db.String(50), nullable=False)
    path_to_portrait = db.Column(db.String(400), nullable=False)
    character_class = db.Column(db.String(10), nullable=False)
    character_level = db.Column(db.Integer, nullable=False)
    character_intelligence = db.Column(db.Integer, nullable=False, default=10)
    character_strength = db.Column(db.Integer, nullable=False, default=10)
    character_dexterity = db.Column(db.Integer, nullable=False, default=10)
    character_base_attack = db.Column(db.Integer, nullable=False, default=10)
    character_hp = db.Column(db.Integer, nullable=False, default=10)
    character_mp = db.Column(db.Integer, nullable=False, default=10)
    character_dodge = db.Column(db.Integer, nullable=False, default=10)


class Skills(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill_name =  db.Column(db.String(50), nullable=False)
    owned_by_class =  db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, default='')
    path_to_icon = db.Column(db.String(400), nullable=False)

@game.route('/')
def index():
    count = 1
    is_newgame = True
    return render_template('main.html', is_newgame=is_newgame, count=count)

@game.route('/signup_page')
def signup_page():
    is_newgame = False
    answer = True
    return render_template('main.html', is_newgame=is_newgame, answer=answer)

@game.route('/login_page')
def login_page():
    is_newgame = False
    answer = False
    return render_template('main.html', is_newgame=is_newgame, answer=answer)

@game.route('/signup', methods=["POST"])
def signup_post():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    # if this returns a user, then email or username already exists in database
    username_taken = Users.query.filter_by(username=username).first()
    user_email_taken = Users.query.filter_by(email=email).first()

    if username_taken: # if a user is found then redirect to registration page
        flash('Username already exists', 'login_error')
        return redirect(url_for('signup_page'))

    if user_email_taken: # if a user is found then redirect to registration page
        flash('Email address already exists', 'email_error')
        return redirect(url_for('signup_page'))

    # Create a new user with form data
    new_user = Users(username=username, email=email, password=generate_password_hash(password, 'sha256'))

    # add a news user to the Users database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login_page'))

@game.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()

        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.', 'data_error')
            return redirect(url_for('login_page'))
        
        login_user(user)
        return redirect(url_for('user_account', username=username))
    else:
        flash(login_manager.login_message, 'not_logged')
        return redirect(url_for('login_page'))

@game.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@game.route('/my/<username>')
@login_required
def user_account(username):
    # Check if user has any characters, if yes - return user main page, if no - return "create character"
    if Users.query.filter_by(username=username).first().characters_list != '':
        character = Characters.query.filter_by(owned_by_user=username).first()
        character_name = character.character_name
        path_to_portrait = character.path_to_portrait
        character_level = character.character_level
        character_class = character.character_class
        character_hp = character.character_hp
        character_mp = character.character_mp
        character_dodge = character.character_dodge
        char_skills = Skills.query.filter_by(owned_by_class=character_class).all()
        skill0 = char_skills[0].skill_name
        skill1 = char_skills[1].skill_name
        skill2 = char_skills[2].skill_name
        skill0_icon = char_skills[0].path_to_icon
        skill1_icon = char_skills[1].path_to_icon
        skill2_icon = char_skills[2].path_to_icon
        skill0_description=char_skills[0].description
        skill1_description=char_skills[1].description
        skill2_description=char_skills[2].description
        character_intelligence = character.character_intelligence
        character_strength = character.character_strength
        character_dexterity = character.character_dexterity

        return render_template('user_page_main.html', 
        username=username, 
        character_name=character_name, 
        path_to_portrait=path_to_portrait, 
        character_level=character_level, 
        character_class=character_class, 
        character_intelligence=character_intelligence, 
        character_strength=character_strength, 
        character_dexterity=character_dexterity,
        character_hp=character_hp,
        character_mp=character_mp,
        character_dodge=character_dodge,
        skill0=skill0, 
        skill1=skill1, 
        skill2=skill2,
        skill0_icon=skill0_icon,
        skill1_icon=skill1_icon,
        skill2_icon=skill2_icon,
        skill0_description=skill0_description,
        skill1_description=skill1_description,
        skill2_description=skill2_description)
    
    return render_template('user_page_create_character.html', username=username)


@game.route('/my/<username>/<chosen_class>', methods=['POST', 'GET'])
@login_required
def create_character(username, chosen_class):
    if request.method == 'GET':
        return render_template(f'characters/base_character.html', username=username, chosen_class=chosen_class)
    else:
        char_name = request.form.get('char_name')
        char_portrait_value = request.form.get('char_portrait')
        char_portrait_path = f'img/{chosen_class}/{char_portrait_value}'
        print(chosen_class)
        if chosen_class == 'mage':
            character_intelligence = 15
            character_strength = 7
            character_dexterity = 7

        if chosen_class == 'warrior':
            character_intelligence = 7
            character_strength = 15
            character_dexterity = 7

        if chosen_class == 'thief':
            character_intelligence = 10
            character_strength = 10
            character_dexterity = 10
          
        new_character = Characters(
            character_name=char_name, 
            owned_by_user=username, 
            character_class=chosen_class, 
            path_to_portrait=char_portrait_path, 
            character_level=1, 
            character_intelligence=character_intelligence, 
            character_strength=character_strength, 
            character_dexterity=character_dexterity, 
            character_hp=character_strength*10,
            character_mp=character_intelligence*10,
            character_dodge=character_dexterity
            )     

        db.session.add(new_character)
        db.session.commit()

        user = Users.query.filter_by(username=username).first()
        char_list = str(user.characters_list) + char_name
        user.characters_list = char_list

        db.session.commit()
        return redirect(url_for('user_account', username=username))




if __name__ == '__main__':
    game.run(debug=True)
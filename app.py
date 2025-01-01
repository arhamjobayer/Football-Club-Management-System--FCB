from flask import Flask, render_template, request, redirect, session, send_file, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import bcrypt
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import re
from flask_share import Share
from werkzeug.utils import secure_filename
import os
from flask_bcrypt import Bcrypt

from functools import wraps
from flask import abort
from flask_login import current_user
from flask_migrate import Migrate


UPLOAD_FOLDER = './static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ADMINUSER = 'admin'
ADMINPASSWORD = 'password12'


share = Share()
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


share.init_app(app)
db = SQLAlchemy(app)
migrate = Migrate(app,db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/admin/login'


app.secret_key = 'secret_key'
bcrypt = Bcrypt()
app.app_context().push()

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/about_us')
def about_us():
    return render_template('about_us.html')


@app.route('/register', methods=['Get', 'POST'])
def register():
    if request.method == 'POST':
        # handle request
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/admin/login', methods=['Get', 'POST'])
def adminLogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = AdminUser.query.filter_by(username=username).first()
        print(user)
        if user:
            if password == user.password:
                login_user(user)
                next = request.args.get('next')
                print(next)
                return redirect(next or url_for('playersAdd'))
            else:
                return render_template('admin-login.html', errorMsg='Invalid Admin Credentials')
        else:
            return render_template('admin-login.html', errorMsg='Invalid Admin Credentials')
    return render_template('admin-login.html', errorMsg='')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = email
            return redirect('/dashboard')
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')

@login_required
@app.route('/dashboard')
def dashboard():
    if session['email']:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html', user=user)

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/login')


@app.route('/admin/logout', methods=['GET', 'POST'])
@login_required
def adminLogout():
    logout_user()
    return redirect('/admin/login')

@login_required
@app.route('/matches')
def allMatches():
    all_matches = Matches.query.order_by(Matches.created_at).all()
    return render_template("matches.html", all_matches=all_matches)


@app.route('/matches/<int:id>')
def matchOne(id):
    match = Matches.query.get_or_404(id)
    return render_template("match-one.html", match=match)

import random
def generate_random_prices():
    x = random.randint(1000, 5000)
    deluxe_seat_price = x * 5
    medium_seat_price = x * 3
    chair_price = x * 2
    return deluxe_seat_price, medium_seat_price, chair_price


@app.route('/buy-ticket/<int:match_id>')

def buy_ticket(match_id):
    # Now you can use the match_id parameter in your function
    match = Matches.query.get_or_404(match_id)
    deluxe_price, medium_price, chair_price = generate_random_prices()
    return render_template('buy_ticket.html', match=match,deluxe_price=deluxe_price, medium_price=medium_price, chair_price=chair_price)

class purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    seat_type = db.Column(db.String(50), nullable=False)
    num_tickets = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    card_number = db.Column(db.String(16), nullable=False)
    cardholder_name = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.String(5), nullable=False)
    security_code = db.Column(db.String(3), nullable=False)

    def __repr__(self):
        return f'<Purchase {self.id}>'

@app.route('/payment/<int:match_id>/<seat_type>', methods=['GET', 'POST'])
def payment(match_id, seat_type):
    match = Matches.query.get_or_404(match_id)
    deluxe_price, medium_price, chair_price = generate_random_prices()

    if request.method == 'POST':
        user_name = request.form['user_name']  # Fix: Get user_name instead of user_id
        card_number = request.form['card_number']
        cardholder_name = request.form['cardholder_name']
        expiry_date = request.form['expiry_date']
        security_code = request.form['security_code']
        num_tickets = int(request.form['num_tickets'])
        total_price = 0

        if seat_type == 'deluxe':
            total_price = deluxe_price * num_tickets
        elif seat_type == 'medium':
            total_price = medium_price * num_tickets
        elif seat_type == 'chair':
            total_price = chair_price * num_tickets

        # Save the purchase information to the database
        new_purchase = purchase(
            user_id=current_user.id,  # Fix: Use user_id instead of user
            match_id=match.id,
            seat_type=seat_type,
            num_tickets=num_tickets,
            total_price=total_price,
            card_number=card_number,
            cardholder_name=cardholder_name,
            expiry_date=expiry_date,
            security_code=security_code
        )
        try:
            db.session.add(new_purchase)  # Fix: Use new_purchase instead of purchase
            db.session.commit()
            return f"Payment successful! You paid ${total_price} for {num_tickets} {seat_type} ticket(s)."
        except Exception as e:
            print(f"Error: {e}")
            return 'An error occurred'

    else:
        return render_template('payment.html', match=match, seat_type=seat_type,
                               deluxe_price=deluxe_price, medium_price=medium_price, chair_price=chair_price)


@app.route('/admin/matches', methods=['POST', 'GET'])
@login_required
def matchesAdd():
    if request.method == "POST":
        team1 = request.form['team1']
        team2 = request.form['team2']
        stadium = request.form['stadium']
        time = request.form['time']
        new_match = Matches(team1=team1, team2=team2,
                            stadium=stadium, time=time)

        try:
            db.session.add(new_match)
            db.session.commit()
            return redirect('/admin/matches')
        except:
            return 'An error occurred'
    else:
        all_matches = Matches.query.order_by(Matches.created_at).all()
        return render_template("match-add.html", all_matches=all_matches)

@app.route('/admin/matches/scrape', methods=['GET'])
@login_required
def matchesScrape():
    html_text = requests.get(
        'https://www.fcbarcelona.com/en/football/first-team/schedule').text
    soup = BeautifulSoup(html_text, 'lxml')
    team1s = soup.find_all('div', class_=re.compile(
        ("^fixture-info__name--home")))
    team2s = soup.find_all('div', class_=re.compile(
        ("^fixture-info__name--away")))
    dates = soup.find_all('div', class_=re.compile(
        ("^fixture-result-list__fixture-date")))
    times = soup.find_all('div', class_=re.compile(("^fixture-info__time")))
    stadiums = soup.find_all('div', class_=re.compile(
        ("^fixture-result-list__stage-location")))

    for team1, team2, date, time, stadium in zip(team1s, team2s, dates, times, stadiums):
        new_match = Matches(team1=team1.text, team2=team2.text,
                            stadium=stadium.text, time=date.text)
        try:
            db.session.add(new_match)
            db.session.commit()
        except:
            return 'An error occurred'
    return redirect('/admin/matches')


@app.route('/admin/matches/delete/<int:id>')
@login_required
def matchDelete(id):
    match_to_delete = Matches.query.get_or_404(id)
    try:
        db.session.delete(match_to_delete)
        db.session.commit()
        return redirect('/admin/matches')
    except:
        return 'An error occurred'


@app.route('/admin/matches/deleteall')
@login_required
def matchDeleteAll():

    try:
        db.session.query(Matches).delete()
        db.session.commit()
        return redirect('/admin/matches')
    except:
        return 'An error occurred'


@app.route('/admin/matches/update/<int:id>', methods=['POST', 'GET'])
@login_required
def matchUpdate(id):
    match_to_update = Matches.query.get_or_404(id)
    if request.method == "POST":
        match_to_update.team1 = request.form['team1']
        match_to_update.team2 = request.form['team2']
        match_to_update.stadium = request.form['stadium']
        match_to_update.time = request.form['time']
        try:
            db.session.commit()
            return redirect('/admin/matches')
        except:
            return 'An error occurred'
    else:
        return render_template("match-update.html", match=match_to_update)


@app.route('/admin/news', methods=['POST', 'GET'])
@login_required
def newsAdd():
    if request.method == "POST":
        news_title = request.form['title']
        news_article = request.form['article']
        new_news = News(title=news_title, article=news_article)

        try:
            db.session.add(new_news)
            db.session.commit()
            return redirect('/admin/news')
        except:
            return 'An error occurred'
    else:
        all_news = News.query.order_by(News.created_at).all()
        return render_template("news-add.html", all_news=all_news)


@app.route('/admin/news/scrape', methods=['GET'])
def newsScrape():
    html_text = requests.get(
        'https://onefootball.com/en/team/barcelona-5').text
    soup = BeautifulSoup(html_text, 'lxml')
    titles = soup.find_all('p', class_=re.compile(
        ("^NewsTeaserV2_teaser__title")))
    teasers = soup.find_all('p', class_=re.compile(
        ("^NewsTeaserV2_teaser__preview")))
    aS = soup.find_all('a', class_=re.compile(
        ("^NewsTeaserV2_teaser__content")))
    for title, url in zip(titles, aS):
        titleText = title.text
        news_html = requests.get('https://onefootball.com' + url['href']).text
        news_soup = BeautifulSoup(news_html, 'lxml')
        article_paragraphs = news_soup.find_all(
            'div', class_=re.compile(("^ArticleParagraph")))
        articleText = ''
        for article in article_paragraphs:
            if article.p:
                articleText += article.p.text
        new_news = News(title=titleText, article=articleText)
        try:
            db.session.add(new_news)
            db.session.commit()
        except:
            return 'An error occurred'
    return redirect('/admin/news')


@app.route('/admin/news/delete/<int:id>')
def newsDelete(id):
    news_to_delete = News.query.get_or_404(id)
    try:
        db.session.delete(news_to_delete)
        db.session.commit()
        return redirect('/admin/news')
    except:
        return 'An error occurred'


@app.route('/admin/news/deleteall')
def newsDeleteAll():
    try:
        db.session.query(News).delete()
        db.session.commit()
        return redirect('/admin/news')
    except:
        return 'An error occurred'


@app.route('/admin/news/update/<int:id>', methods=['POST', 'GET'])
def newsUpdate(id):
    news_to_update = News.query.get_or_404(id)
    if request.method == "POST":
        news_to_update.title = request.form['title']
        news_to_update.article = request.form['article']
        try:
            db.session.commit()
            return redirect('/admin/news')
        except:
            return 'An error occurred'
    else:
        return render_template("news-update.html", news=news_to_update)


@app.route('/news')
def allNews():
    all_news = News.query.order_by(News.created_at).all()
    return render_template("news.html", all_news=all_news)


@app.route('/news/<int:id>')
def newsOne(id):
    news = News.query.get_or_404(id)
    return render_template("news-one.html", news=news)


@app.route('/admin/players', methods=['POST', 'GET'])
@login_required
def playersAdd():
    if request.method == "POST":
        name = request.form['name']
        age = request.form['age']
        height = request.form['height']
        image = request.files['image']
        weight = request.form['weight']
        nationality = request.form['nationality']
        jersey_no = request.form['jersey_no']
        position = request.form['position']
        match_played = request.form['match_played']
        goals = request.form['goals']
        assists = request.form['assists']
        file_url = ''
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_url = filename
        new_player = Player(name=name, age=age, height=height, weight=weight, nationality = nationality,
                            jersey_no=jersey_no, position=position, imageFile=file_url, match_played=match_played, goals=goals, assists=assists)

        try:
            db.session.add(new_player)
            db.session.commit()
            return redirect('/admin/players')
        except:
            return 'An error occurred'
        pass
    else:
        all_players = Player.query.order_by(Player.created_at).all()
        return render_template("player-add.html", all_players=all_players)


@app.route('/admin/players/update/<int:id>', methods=['POST', 'GET'])
def playerUpdate(id):
    player_to_update = Player.query.get_or_404(id)
    if request.method == "POST":
        player_to_update.name = request.form['name']
        player_to_update.age = request.form['age']
        player_to_update.height = request.form['height']
        player_to_update.weight = request.form['weight']
        player_to_update.nationality = request.form['nationality']
        player_to_update.jersey_no = request.form['jersey_no']
        player_to_update.position = request.form['position']
        player_to_update.match_played = request.form['match_played']
        player_to_update.goals = request.form['goals']
        player_to_update.assists = request.form['assists']
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            player_to_update.imageFile = filename
        try:
            db.session.commit()
            return redirect('/admin/players')
        except:
            return 'An error occurred'
    else:
        return render_template("player-update.html", player=player_to_update)


@app.route('/admin/players/delete/<int:id>')
def playerDelete(id):
    player_to_delete = Player.query.get_or_404(id)
    try:
        db.session.delete(player_to_delete)
        db.session.commit()
        return redirect('/admin/players')
    except:
        return 'An error occurred'


@app.route('/players')

def allPlayers():
    all_players = Player.query.order_by(Player.created_at).all()
    return render_template("players.html", all_players=all_players)

@app.route('/allproduct')
def allproduct():
    allproduct = Shop.query.order_by(Shop.created_at).all()
    return render_template("products.html", allproduct=allproduct)

@app.route('/players/<int:id>')
def playerOne(id):
    player = Player.query.get_or_404(id)
    return render_template("player-one.html", player=player)


@app.route('/team')
def team():
    return render_template("team.html")

@app.route('/done_payment_2', methods=['POST', 'GET'])
def payment2():
    return render_template('done_payment_2.html')

@app.route('/admin/shop', methods=['POST', 'GET'])
@login_required
def shopAdd():
    if request.method == "POST":
        name = request.form['name']
        image = request.files['image']
        price = request.form['price']
        jersey_no = request.form['jersey_no']
        file_url = ''

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_url = filename

        new_product = Shop(name=name, imageFile=file_url, price=price, jersey_no=jersey_no)

        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect('/admin/shop')
        except:
            return 'An error occurred'

    else:
        all_products = Shop.query.order_by(Shop.created_at).all()
        return render_template("shop-add.html", all_products=all_products)

@app.route('/admin/shop/update/<int:id>', methods=['GET', 'POST'])
def update_product(id):
    product = Shop.query.get_or_404(id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        product.jersey_no = request.form['jersey_no']

        # Save the changes to the database
        db.session.commit()
        return redirect('/admin/shop')

    return render_template('update-product.html', product=product)


@app.route('/admin/shop/delete/<int:id>', methods=['POST'])
def delete_product(id):
    product = Shop.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect('/admin/shop')

@app.route('/product/<int:product_id>/')
def product_detail(product_id):
    product = Shop.query.get(product_id)
    return render_template('product_detail.html', product=product)

from flask import jsonify

score = 0

@app.route('/football_game', methods=['GET', 'POST'])
def football_game():
    global score
    if request.method == 'POST':
        score += 1
        return jsonify({'score': score, 'html': render_template('football_game.html', score=score)})
    else:
        # Handle GET request (e.g., render the initial HTML page)
        return render_template('football_game.html', score=score)


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    article = db.Column(db.String(1000), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<News %r>' % self.id


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    age = db.Column(db.String(200), nullable=True)
    weight = db.Column(db.String(200), nullable=True)
    height = db.Column(db.String(200), nullable=True)
    imageFile = db.Column(db.String(200), nullable=True)
    nationality = db.Column(db.String(200), nullable=True)
    jersey_no = db.Column(db.String(200), nullable=True)
    position = db.Column(db.String(200), nullable=True)
    match_played = db.Column(db.String(200), nullable=True)
    goals = db.Column(db.String(200), nullable=True)
    assists = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Player %r>' % self.id
class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    imageFile = db.Column(db.String(200), nullable=True)
    price = db.Column(db.String(200), nullable=True)
    jersey_no = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Player %r>' % self.id

class Matches(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team1 = db.Column(db.String(200), nullable=True)
    team2 = db.Column(db.String(200), nullable=True)
    stadium = db.Column(db.String(200), nullable=True)
    time = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Matches %r>' % self.id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, email, password, name):
        self.name = name
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


class AdminUser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


if __name__ == "__main__":
    app.run(debug=True)
    db.create_all()
    admin = AdminUser.query.get(1)
    if admin:
        pass
    else:
        new_user = AdminUser(username=ADMINUSER, password=ADMINPASSWORD)
        db.session.add(new_user)
        db.session.commit()
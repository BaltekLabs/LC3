from flask import Flask, request, render_template, redirect, url_for, session
import requests
import io
from flask_pymongo import PyMongo
import bcrypt
import jsonify

#import csv
#from lightmatchingengine.lightmatchingengine import LightMatchingEngine, Side
import pandas as pd
#lme = LightMatchingEngine()


# APP CONFIG
app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'mongologinexample'
app.config['MONGO_URI'] = 'mongodb://pretty:printed@ds021731.mlab.com:21731/mongologinexample'

mongo = PyMongo(app)


# PAGE ROUTES

@app.route("/")
def index():
    if 'username' in session:
        return 'You are logged in as ' + session['username']

    return render_template('/index.html')

@app.route('/homeLanding')
def home():
    return render_template('/homeLanding.html')

@app.route('/userLanding')
def userLanding():
    return render_template('/userLanding.html')

@app.route('/falseIdent')
def falseIdent():
    return render_template('/homelandingNullLogin.html')

@app.route('/profile')
def profile():
    user_name = session.get('user_name',None)
    return render_template('/extras-profile.html',user_name=user_name)

@app.route('/research')
def research():
    return render_template('research.html')

@app.route('/calendar')
def calendar():
     return render_template('calendar.html')

@app.route('/messageBox')
def messageBox():
    return render_template('/email-inbox.html')

@app.route('/stockData')
def stockData():
    return render_template('/stockData.html')

# FORM ROUTES

@app.route('/userHome', methods=['GET','POST'])
def userHome():
    user_num = "0"
    user_name = "User"
    if request.method == 'POST':
        user_num = request.form['user_id']
        
    if user_num == "1":
           user_name  = "William"
    else:
        return redirect('/falseIdent')
    session['user_name']= user_name   
    return render_template('/user-main.html', user_name=user_name)
        
@app.route('/dashboard', methods=['POST','GET'])
def dashboard():
    API_KEY = '8XTSMCVVBO5CJLT9'
    #if request.method == 'POST':
#        stock_request = request.form['stock_search'] 
    r = requests.get('https://www.alphavantage.co/query?function=BATCH_STOCK_QUOTES&symbols=BA,AAPL,MMM&apikey='+ API_KEY)
    ba = requests.get('https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=BA&apikey='+ API_KEY)
    aapl = requests.get('https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey='+ API_KEY)
    mmm = requests.get('https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=MMM&apikey='+ API_KEY)
    
    res = r.json()
    ba_res = ba.json()
    aapl_res = aapl.json()
    mmm_res = mmm.json()
   
    data = res['Stock Quotes']
    ba_global = ba_res['Global Quote']
    aapl_global = aapl_res['Global Quote']
    mmm_global = mmm_res['Global Quote']


    BA_data = data[0]
    AAPL_data = data[1]
    MMM_data = data[2]

    ba_symbol = BA_data['1. symbol']
    ba_change = ba_global['10. change percent']
    aapl_symbol = AAPL_data['1. symbol']
    mmm_symbol = MMM_data['1. symbol']
    ba_price = BA_data['2. price']
    aapl_price = AAPL_data['2. price']
    mmm_price = MMM_data['2. price']
    #session['stock_open'] = data['open']
    #session['high'] = data['high']
    #session['low'] = data['low']
    
    #session['volume'] = data['volume']
    #change = data['09. change']

    ba_chart_close = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=BA&interval=5min&apikey=8XTSMCVVBO5CJLT9&datatype=csv')
    df = pd.read_csv(io.StringIO(ba_chart_close.text))
    #df.to_csv('intra.csv')
    #close_csv_feed = pd.read_csv('intra.csv')
    for x in df.index:
        df.rename(index={x+1: ','}, inplace=True)
    
    df.rename(index={0: ' '}, inplace=True)
    ba_chart_prices = df.close.values
    for val in ba_chart_prices:
        new_val = '%s'%val+ ','
    
   # for val in ba_chart_prices:
    #    new_val = '%s'%val + ','
    chart_vals= new_val
    return render_template('/index.html', ba_symbol=ba_symbol,ba_price=ba_price,ba_change=ba_change,aapl_symbol=aapl_symbol,aapl_price=aapl_price,mmm_symbol=mmm_symbol,mmm_price=mmm_price,chart_vals=chart_vals )
        #return render_template('/page-login.html', symbol=session['symbol'], open=session['stock_open'], high=session['high'],low=session['low'], price=session['price'],volume=session['volume'], change=session['change'] )
        
@app.route('/buyEntered', methods=['GET','POST'])
def buyEntered():
    if request.method == 'POST':
        stock_request = session.get('stock_request',None)
        stock_data = session.get('stock_data', None)
        order_size = request.form['order_size']
        order_price = request.form['order_price']
       # order_type = request.form['order_type']
       # order, trades = lme.add_order(stock_request, order_price, order_size, Side.BUY)
        order = [stock_request, order_price, order_size, "buy"]
        with open("order.txt","w") as fo:
            fo.writelines(repr(order))

        
        return render_template('/stockData.html', stock_request= stock_request, stock_data = stock_data)



#USER AUTHENTIFICATION 

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = request.form['username']
            return redirect(url_for('/'))

    return 'Invalid username/password combination'

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        
        return 'That username already exists!'

    return render_template('page-register.html')






#Functions

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)

    

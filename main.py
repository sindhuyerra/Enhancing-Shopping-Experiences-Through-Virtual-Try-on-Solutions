#!/usr/bin/env python3
# from tryOn import TryOn as tryOn

# E-dressing lo backend
# virtualtril lo frontend 

from flask import Flask, render_template, Response,redirect,request,url_for,flash,get_flashed_messages,session
from camera import VideoCamera
import os
import mysql.connector
import stripe


app = Flask(__name__)
app.secret_key=b'codegnas$#@key^*^&*^&*^&7e63463ruwyasgdjs*^*^&^&'
stripe.api_key='sk_test_51OtAJqSCk2KOogz2u2Uip6e6tMdinX0y4iMm4hcfUHOYdiGf4fXe5IatEcuQiog3cNGG0DHpG5G0EhoOmtbspPD000vmfQDSiw'
CART=[]

mydb = mysql.connector.connect(host='localhost',
                               user='root',
                               password='admin',
                               db='trail')

@app.route('/checkOut')
def checkOut():
    print('in checkout route')
    return render_template('checkout.html')

#created by saketh garu
@app.route('/',methods=['POST','GET'])
def create():
    if session.get('user'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        #print(request.form)
        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        #cpassword=request.form['CPassword']
        print(name,email,password)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('insert into user (name,Email,password) values(%s,%s,%s)',(name,email,password))
        cursor.close()
        mydb.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login',methods = ['POST', 'GET'])
def login():
    if session.get('user'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        email=request.form['Email']
        password=request.form['Password']
        #print(email,password)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select email,password from user where Email=%s',[email])
        user,pwd= cursor.fetchone()
        cursor.close()
        #print(user,pwd)
        if user == email and pwd == password:
            session['user'] = email
            flash('Login successfull...!')
            return redirect(url_for('index'))
        else:
            flash('Invalide user or password...!')
            return render_template('login.html')
    return render_template('login.html')


@app.route('/tryon/<file_path>',methods = ['POST', 'GET'])
def tryon(file_path):
    if not session.get('user'):
        return redirect(url_for('login'))
    file_path = file_path.replace(',','/')
    os.system('python tryOn.py ' + file_path)
    print('-------------',os.system('python tryOn.py ' + file_path))
    return redirect(url_for('index'),code=302, Response=None)

@app.route('/tryall',methods = ['POST', 'GET'])
def tryall():
    if not session.get('user'):
        return redirect(url_for('login'))
    print("YESSS")
    if request.method == 'POST':
        cart = request.form['mydata'].replace(',', '/')
        print(cart)
        os.system('python test.py ' + cart)
    return  render_template('checkout.html', message='')

@app.route('/pay/<name>/<int:price>')
def pay(name,price):
    if not session.get('user'):
        return redirect(url_for('login'))
    q=price
    total=price
    checkout_session=stripe.checkout.Session.create(
        success_url=url_for('success',item=name,qty=q,total=total,_external=True),
        line_items=[
                {
                    'price_data': {
                        'product_data': {
                            'name': name,
                        },
                        'unit_amount': price*100,
                        'currency': 'inr',
                    },
                    'quantity': q,
                },
                ],
        mode="payment",)
    return redirect(checkout_session.url)
@app.route('/success/<item>/<qty>/<total>')
def success(item,qty,total):
    if not session.get('user'):
        return redirect(url_for('login'))
    return {'item':item,'quantity':qty,'total':total}


@app.route('/index')
def index():
    if not session.get('user'):
        return redirect(url_for('login'))
    print('hello')
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route("/cart/<file_path>",methods = ['POST', 'GET'])
def cart(file_path):
    if not session.get('user'):
        return redirect(url_for('login'))
    global CART
    file_path = file_path.replace(',','/')
    print("ADDED", file_path)
    CART.append(file_path)
    return render_template("checkout.html")

@app.route('/video_feed')
def video_feed():
    if not session.get('user'):
        return redirect(url_for('login'))
    return Response(gen(VideoCamera()),mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('login'))
    else:
        flash("Please login to continue")
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True,use_reloader=True)
    

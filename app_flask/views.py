# -*- encoding=UTF-8 -*-
from app_flask import app,db
from qiniusdk import qiniu_upload_file
from flask import render_template,redirect,request,flash,get_flashed_messages
from models import Image,User,Comment
import random,hashlib,uuid,os
from flask_login import login_user,logout_user,current_user,login_required

@app.route('/')
def index():
    image = Image.query.order_by(Image.id).limit(10).all()
    return render_template('index.html',images=image)

@app.route('/regloginpage/')
def regloginpage():
    msg=''
    for m in get_flashed_messages(with_categories=False,category_filter=['reglogin']):
        msg =msg + m
    return render_template('login.html',msg=msg ,next=request.values.get('next'))

def redirect_with_message(target ,msg,category):
    if msg != None:
        flash(msg,category=category)
    return redirect(target)

@app.route('/reg/',methods={'post','get'})
def reg():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    if username=="" or password=="":
        return redirect_with_message('/regloginpage',u'用户名密码不能为空','reglogin')

    user = User.query.filter_by(username=username).first()
    if user != None:
        return redirect_with_message('/regloginpage',u'用户已存在','reglogin')

    salt = '.'.join(random.sample('0123456789abecdefghABCEDFGHI',10))
    m = hashlib.md5()
    m.update(password+salt)
    password=m.hexdigest()
    user = User(username,password,salt)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    next = request.values.get('next')
    if next != None and next.startswith('/'):
        return redirect(next)
    return redirect('/')

@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')

@app.route('/image/<int:image_id>')
@login_required
def image(image_id):
    image = Image.query.get(image_id)
    comment= Comment.query.filter_by(image_id=image_id).all()
    return render_template('pageDetail.html',image =image,comments=comment)

@app.route('/login/',methods={'post','get'})
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    if username == "" or password == "":
        return redirect_with_message('/regloginpage', u'用户名密码不能为空', 'reglogin')

    user = User.query.filter_by(username=username).first()
    if user == None:
        redirect_with_message('/regloginpage', u'用户不存在', 'reglogin')
    m = hashlib.md5()
    m.update(password + user.salt)
    if user.password != m.hexdigest() :
        return redirect_with_message('/regloginpage', u'密码错误', 'reglogin')

    login_user(user)
    next = request.values.get('next')
    if next != None and next.startswith('/'):
        return redirect(next)
    return redirect('/')

@app.route('/profile/<int:user_id>/')
def profile(user_id):
    user = User.query.get(user_id)
    if user ==None:
        return redirect('/')
    image = Image.query.filter_by(user_id = user_id).order_by(Image.id).paginate(page=1, per_page=3,error_out=False)
    return render_template('profile.html',user=user,images=image.items,has_next=image.has_next)

@app.route('/upload/',methods={'post'})
@login_required
def upload():
    file = request.files['file']
    file_ext=''
    if file.filename.find('.') > 0:
        file_ext = str(file.filename.rsplit('.',1)[1]).strip().lower()

    if file_ext in app.config['ALLOWED_EXT']:
        file_name = str(uuid.uuid1()).replace('-','') + '.' + file_ext
        url=qiniu_upload_file(file,file_name)
        if url != None :
            db.session.add(Image(url,current_user.id))
            db.session.commit()

    return redirect('/profile/%d'% current_user.id)
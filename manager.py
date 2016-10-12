# -*- encoding=UTF-8 -*-

from app_flask import app,db
from flask_script import  Manager
from app_flask.models import User,Image,Comment
import random
manger = Manager(app)

def get_image_url():
    return 'http://images.nowcoder.com/head/'+str(random.randint(0,1000))+'m.png'

@manger.command
def init_database():
    db.drop_all()
    db.create_all()
    for i in range(0,100):
        db.session.add(User('User'+str(i),'a'+str(i)))
        for j in range(0,3):
            db.session.add(Image(get_image_url(),i+1))
            for k in range(0,3):
                db.session.add(Comment('This is comment' +str(k) , 1+3*i+j,i+1))
    db.session.commit()
    for i in range(50,100,2):
        user=User.query.get(i)
        user.username='[New]'+user.username

    User.query.filter_by(id=51).update({'username':'[new2]'})

    db.session.commit()


if  __name__ =='__main__':
    manger.run();
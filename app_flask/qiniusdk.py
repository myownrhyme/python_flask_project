# -*- coding :UTF-8 -*-
from app_flask import  app
from qiniu import Auth, put_data
import qiniu.config
import os
from uuid import uuid1

access_key = app.config['QINIU_ACCESS_KEY']
secret_key = app.config['QINIU_SERECT_KEY']

q = Auth(access_key, secret_key)


bucket_name = app.config['QINIU_BUCKET_NAME']
domain_prefix = app.config['QINIU_DOMAIN_PREFIX']

def qiniu_upload_file(source_file,save_file_name):
    token = q.upload_token(bucket_name, save_file_name)
    print type(domain_prefix), type(save_file_name),domain_prefix,save_file_name
    ret, info = put_data(token, save_file_name, source_file.stream)

    if info.status_code == 200:

        return domain_prefix+save_file_name
    return None

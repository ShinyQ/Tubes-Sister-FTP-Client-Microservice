from fastapi import FastAPI, Response, UploadFile, File
from pydantic import BaseModel

import api
import json
import xmlrpc.client as client

server = client.ServerProxy("http://127.0.0.1:1717/")

app = FastAPI()


class User(BaseModel):
    username: str
    password: str


class UserUploadFile(BaseModel):
    username: str
    password: str
    filename: str
    file: UploadFile = File(...)


class UserDownloadFile(BaseModel):
    username: str
    password: str
    uuid_file: str


@app.post('/login', status_code=200)
def login(response: Response, user: User):
    res = server.login(user.username, user.password)
    res = json.loads(res)

    if not res.get('success'):
        data = []
        response.status_code = 500
    else:
        data = res.get('data')

    return api.builder(data, response.status_code)


@app.post('/register', status_code=200)
def register(response: Response, user: User):
    res = server.register(user.username, user.password)
    res = json.loads(res)

    if not res.get('success'):
        response.status_code = 500

    return api.builder([], response.status_code)


@app.get('/file_list', status_code=200)
def file_list(response: Response):
    # TODO : Menampilkan Seluruh File Via RPC
    data = ''
    return api.builder(data, response.status_code)


@app.get('/user_file_list', status_code=200)
def user_file_list(response: Response, user: User):
    # TODO 1: Login Duls Via RPC
    # TODO 2: Menampilkan Seluruh File Milik user Via RPC
    data = ''
    return api.builder(data, response.status_code)


@app.post('/upload_file', status_code=200)
def upload_file(response: Response, user: UserUploadFile):
    # TODO 1: Login Duls Via RPC
    # TODO 2: Mengupload File Milik user Via RPC
    data = ''
    return api.builder(data, response.status_code)


@app.get('/download_file', status_code=200)
def download_file(response: Response, user: UserDownloadFile):
    # TODO 1: Login Duls Via RPC
    # TODO 2: Download Dan Simpan File Milik user Via RPC Ke Folder File
    # TODO 3: Return Json Link File
    data = ''
    return api.builder(data, response.status_code)


@app.get('/most_active', status_code=200)
def most_active(response: Response):
    # TODO 1: Get Most Active User
    data = ''
    return api.builder(data, response.status_code)

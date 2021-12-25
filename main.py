from fastapi import FastAPI, Response, UploadFile, File, Form, Depends
from pydantic import BaseModel

import api
import json
import xmlrpc.client as client

server = client.ServerProxy("https://rpc.krobot.my.id/")

app = FastAPI()


def form_body(cls):
    cls.__signature__ = cls.__signature__.replace(
        parameters=[
            arg.replace(default=Form(...))
            for arg in cls.__signature__.parameters.values()
        ]
    )
    return cls


class User(BaseModel):
    username: str
    password: str


@form_body
class UserUploadFile(BaseModel):
    username: str
    password: str
    filename: str


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
    data = json.loads(server.file_list()).get('data')
    return api.builder(data, response.status_code)


@app.post('/user_file_list', status_code=200)
def user_file_list(response: Response, user: User):
    res = server.login(user.username, user.password)
    res = json.loads(res)

    res = server.my_files(res.get('data').get('id'))
    res = json.loads(res)

    data = res.get('data')
    return api.builder(data, response.status_code)


@app.post('/upload_file', status_code=200)
async def upload_file(response: Response, user: UserUploadFile = Depends(UserUploadFile), file: UploadFile = File(...)):
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

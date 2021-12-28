from fastapi import FastAPI, Response, UploadFile, File, Form, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime

import api
import json
import base64
import xmlrpc.client as client

server = client.ServerProxy("https://rpc.krobot.my.id/")

app = FastAPI()
app.mount("/files", StaticFiles(directory="files"), name="files")


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
class UserDetail(BaseModel):
    id: str


class UserDownloadFile(BaseModel):
    id: str
    uuid_file: str


@app.post("/login", status_code=200)
def login(response: Response, user: User):
    res = server.login(user.username, user.password)
    res = json.loads(res)

    if not res.get("success"):
        data = []
        response.status_code = 500
    else:
        data = res.get("data")

    return api.builder(data, response.status_code)


@app.post("/register", status_code=200)
def register(response: Response, user: User):
    res = server.register(user.username, user.password)
    res = json.loads(res)

    if not res.get("success"):
        response.status_code = 500

    return api.builder([], response.status_code)


@app.get("/file_list", status_code=200)
def file_list(response: Response):
    data = json.loads(server.file_list()).get("data")
    return api.builder(data, response.status_code)


@app.post("/user_file_list", status_code=200)
def user_file_list(response: Response, user: UserDetail):
    res = server.my_files(user.id)
    res = json.loads(res)

    data = res.get("data")
    return api.builder(data, response.status_code)


@app.post("/upload_file", status_code=200)
async def upload_file(
        response: Response,
        user: UserDetail = Depends(UserDetail),
        file: UploadFile = File(...),
):
    data = client.Binary(await file.read())
    server.file_upload(data, file.filename, user.id)

    return api.builder([], response.status_code)


@app.post("/download_file", status_code=200)
def download_file(response: Response, user: UserDownloadFile):
    res = server.file_download(user.id, user.uuid_file)
    res = json.loads(res)

    if res.get("success"):
        filename = res["data"]["fileName"]
        saved_filename = "{}_{}".format(datetime.now().strftime("%y%m%d_%H%M%S"), filename)
        file_location = "files/{}".format(saved_filename)

        with open(file_location, "wb") as handle:
            handle.write(base64.b64decode(res["data"]["fileData"]))
            handle.close()
    else:
        return api.builder([], 500)

    return api.builder(saved_filename, response.status_code)


@app.get("/most_active_upload", status_code=200)
def most_active_upload(response: Response):
    res = server.most_active("upload")
    res = json.loads(res)

    if not res.get("success"):
        data = []
        response.status_code = 500
    else:
        data = res.get("data")

    return api.builder(data, response.status_code)


@app.get("/most_active_download", status_code=200)
def most_active_download(response: Response):
    res = server.most_active("download")
    res = json.loads(res)

    if not res.get("success"):
        data = []
        response.status_code = 500
    else:
        data = res.get("data")

    return api.builder(data, response.status_code)


@app.get("/logs_download", status_code=200)
def logs_download(response: Response):
    res = server.logs("download")
    res = json.loads(res)

    if not res.get("success"):
        data = []
        response.status_code = 500
    else:
        data = res.get("data")

    return api.builder(data, response.status_code)


@app.get("/logs_upload", status_code=200)
def logs_upload(response: Response):
    res = server.logs("upload")
    res = json.loads(res)

    if not res.get("success"):
        data = []
        response.status_code = 500
    else:
        data = res.get("data")

    return api.builder(data, response.status_code)


@app.get("/logs_all", status_code=200)
def logs_all(response: Response):
    res = server.logs()
    res = json.loads(res)

    if not res.get("success"):
        data = []
        response.status_code = 500
    else:
        data = res.get("data")

    return api.builder(data, response.status_code)


@app.get("/logs_data", status_code=200)
def logs_data(response: Response):
    res = server.log_data()
    res = json.loads(res)

    if not res.get("success"):
        data = []
        response.status_code = 500
    else:
        data = res.get("data")

    return api.builder(data, response.status_code)


@app.get("/get_users", status_code=200)
def get_users(response: Response):
    res = server.get_users()
    res = json.loads(res)

    if not res.get("success"):
        data = []
        response.status_code = 500
    else:
        data = res.get("data")

    return api.builder(data, response.status_code)
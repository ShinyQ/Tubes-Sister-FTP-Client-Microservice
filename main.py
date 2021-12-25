from fastapi import FastAPI, Response, UploadFile, File, Form, Depends
from pydantic import BaseModel
from datetime import datetime

from starlette.responses import FileResponse

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
    file.filename = file.filename
    with open(file.filename, "rb") as handle:
        data = client.Binary(handle.read())
        res = server.file_upload(data, file.filename, user.id)

    return api.builder([], response.status_code)


@app.post("/download_file", status_code=200)
def download_file(response: Response, user: UserDownloadFile):
    res = server.file_download(user.id, user.uuid_file)
    res = json.loads(res)
    if res.get("success"):
        filename = res["data"]["fileName"]
        saved_filename = "{}_{}".format(
            datetime.now().strftime("%y%m%d_%H%M%S"),
            filename,
        )
        file_location = "files/{}".format(saved_filename)
        with open(file_location, "wb") as handle:
            handle.write(bytes(res["data"]["fileData"], "utf-8"))
            handle.close()
    else:
        return api.builder([], 500)

    return FileResponse(
        file_location, media_type="application/octet-stream", filename=filename
    )


@app.get("/most_active", status_code=200)
def most_active(response: Response):
    res = server.most_active()
    res = json.loads(res)

    if not res.get("success"):
        data = []
        response.status_code = 500
    else:
        data = res.get("data")

    return api.builder(data, response.status_code)

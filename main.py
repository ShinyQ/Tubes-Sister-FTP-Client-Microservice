# Import Library yang dibutuhkan
from fastapi import FastAPI, Response, UploadFile, File, Form, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime

import api
import json
import base64
import xmlrpc.client as client

# Mendefenisikan variabel Client yang mengarah pada Server
# yang telah dibuat.
Client = client.ServerProxy("https://rpc.krobot.my.id/")

# Memanggil library FastApi()
app = FastAPI()
app.mount("/files", StaticFiles(directory="files"), name="files")

# Membuat function form_body
def form_body(cls):
    cls.__signature__ = cls.__signature__.replace(
        parameters=[
            arg.replace(default=Form(...))
            for arg in cls.__signature__.parameters.values()
        ]
    )
    return cls


# Membuat class user dengan parameter BaseModel
# yang berisi username dan password user
class User(BaseModel):
    username: str
    password: str


# Membuat class UserDetail dengan parameter BaseModel
# yang berisi id user
@form_body
class UserDetail(BaseModel):
    id: str


# Membuat class UserDownloadFile dengan parameter BaseModel
# yang berisi id user dan uuid file
class UserDownloadFile(BaseModel):
    id: str
    uuid_file: str


# Membuat function login dengan inputan username dan password
# dari user.
@app.post("/login", status_code=200)
def login(response: Response, user: User):
    # Memanggil fungsi login pada client yang telah
    # didefinisikan di server.
    res = Client.login(user.username, user.password)
    # Mengubah tipe data menjadi json
    res = json.loads(res)

    # Jika tidak berhasil, maka data akan bernilai kosong
    # dan mengubah status_code menjadi 500
    if not res.get("success"):
        data = []
        response.status_code = 500
    else:
        data = res.get("data")

    return api.builder(data, response.status_code)


# Membuat function register dengan inputan username dan password
@app.post("/register", status_code=200)
def register(response: Response, user: User):
    # Memanggil fungsi register pada client yang telah
    # didefinisikan di server.
    res = Client.register(user.username, user.password)
    # Mengubah tipe data menjadi json
    res = json.loads(res)

    # Jika tidak berhasil, maka status_code diubah menjadi 500
    if not res.get("success"):
        response.status_code = 500

    return api.builder([], response.status_code)


# Membuat function file_list yang akan mengembalikan
# semua file yang telah diupload oleh semua user
@app.get("/file_list", status_code=200)
def file_list(response: Response):
    # Melakukan load data dari client.file_list()
    data = json.loads(Client.file_list()).get("data")
    return api.builder(data, response.status_code)


# Membuat function user_file_list yang akan mengembalikan
# semua file yang telah diupload oleh user yang bersangkutan
@app.post("/user_file_list", status_code=200)
def user_file_list(response: Response, user: UserDetail):
    # Memanggil fungsi my_files pada client yang telah
    # didefinisikan di server
    res = Client.my_files(user.id)
    # Mengubah tipe data menjadi json
    res = json.loads(res)

    # Mengambil data pada variabel res
    data = res.get("data")
    return api.builder(data, response.status_code)


# Membuat function upload_file agar user dapat melakukan
# upload file.
@app.post("/upload_file", status_code=200)
async def upload_file(
    response: Response,
    user: UserDetail = Depends(UserDetail),
    file: UploadFile = File(...),
):
    data = client.Binary(await file.read())
    # Memanggil fungsi file_upload pada client yang telah
    # didefinisikan di server
    Client.file_upload(data, file.filename, user.id)

    return api.builder([], response.status_code)


# Membuat function download_file agar user dapat melakukan
# download file.
@app.post("/download_file", status_code=200)
def download_file(response: Response, user: UserDownloadFile):
    # Memanggil fungsi file_download pada client yang telah
    # didefinisikan di server dengan parameter user.id dan
    # uuid_file yang ingin didownload
    res = Client.file_download(user.id, user.uuid_file)
    # Mengubah tipe data menjadi json
    res = json.loads(res)

    if res.get("success"):
        # Jika download berhasil, maka filename akan diset
        # unik agar tidak terjadi file lain yang tertimpa
        filename = res["data"]["fileName"]
        saved_filename = "{}_{}".format(
            datetime.now().strftime("%y%m%d_%H%M%S"), filename
        )
        # file akan disimpan pada folder files
        file_location = "files/{}".format(saved_filename)

        with open(file_location, "wb") as handle:
            handle.write(base64.b64decode(res["data"]["fileData"]))
            handle.close()
    else:
        return api.builder([], 500)

    return api.builder(saved_filename, response.status_code)


# Membuat function most_active_upload untuk melihat
# user dengan upload terbanyak
@app.get("/most_active_upload", status_code=200)
def most_active_upload(response: Response):
    # Memanggil fungsi most_active pada client yang telah
    # didefinisikan di server
    res = Client.most_active("upload")
    # Mengubah tipe data menjadi json
    res = json.loads(res)

    # Jika tidak berhasil, maka data akan bernilai kosong
    # dan mengubah status_code menjadi 500
    if not res.get("success"):
        data = []
        response.status_code = 500
    else:
        data = res.get("data")

    return api.builder(data, response.status_code)


# Membuat function most_active_download untuk melihat
# user dengan download terbanyak
@app.get("/most_active_download", status_code=200)
def most_active_download(response: Response):
    # Memanggil fungsi most_active pada client yang telah
    # didefinisikan di server
    res = Client.most_active("download")
    # Mengubah tipe data menjadi json
    res = json.loads(res)

    # Jika tidak berhasil, maka data akan bernilai kosong
    # dan mengubah status_code menjadi 500
    if not res.get("success"):
        data = []
        response.status_code = 500
    else:
        data = res.get("data")

    return api.builder(data, response.status_code)


# Membuat function logs_download untuk melihat
# log download yang dilakukan oleh semua user
@app.get("/logs_download", status_code=200)
def logs_download(response: Response):
    # Memanggil fungsi logs pada client yang telah
    # didefinisikan di server
    res = Client.logs("download")
    # Mengubah tipe data menjadi json
    res = json.loads(res)

    # Jika tidak berhasil, maka data akan bernilai kosong
    # dan mengubah status_code menjadi 500
    if not res.get("success"):
        data = []
        response.status_code = 500
    else:
        data = res.get("data")

    return api.builder(data, response.status_code)


# Membuat function logs_upload untuk melihat
# log upload yang dilakukan oleh semua user
@app.get("/logs_upload", status_code=200)
def logs_upload(response: Response):
    # Memanggil fungsi logs pada client yang telah
    # didefinisikan di server
    res = Client.logs("upload")
    # Mengubah tipe data menjadi json
    res = json.loads(res)

    # Jika tidak berhasil, maka data akan bernilai kosong
    # dan mengubah status_code menjadi 500
    if not res.get("success"):
        data = []
        response.status_code = 500
    else:
        data = res.get("data")

    return api.builder(data, response.status_code)


# Membuat function logs_all untuk melihat
# log upload dan log download yang dilakukan oleh semua user
@app.get("/logs_all", status_code=200)
def logs_all(response: Response):
    # Memanggil fungsi logs pada client yang telah
    # didefinisikan di server
    res = Client.logs()
    # Mengubah tipe data menjadi json
    res = json.loads(res)

    # Jika tidak berhasil, maka data akan bernilai kosong
    # dan mengubah status_code menjadi 500
    if not res.get("success"):
        data = []
        response.status_code = 500
    else:
        data = res.get("data")

    return api.builder(data, response.status_code)


# Membuat function logs_data
@app.get("/logs_data", status_code=200)
def logs_data(response: Response):
    # Memanggil fungsi log_data pada client yang telah
    # didefinisikan di server
    res = Client.log_data()
    # Mengubah tipe data menjadi json
    res = json.loads(res)

    # Jika tidak berhasil, maka data akan bernilai kosong
    # dan mengubah status_code menjadi 500
    if not res.get("success"):
        data = []
        response.status_code = 500
    else:
        data = res.get("data")

    return api.builder(data, response.status_code)


# Membuat function get_users untuk melihat semua user
# yang terdaftar pada sistem.
@app.get("/get_users", status_code=200)
def get_users(response: Response):
    # Memanggil fungsi get_users pada client yang telah
    # didefinisikan di server
    res = Client.get_users()
    # Mengubah tipe data menjadi json
    res = json.loads(res)

    # Jika tidak berhasil, maka data akan bernilai kosong
    # dan mengubah status_code menjadi 500
    if not res.get("success"):
        data = []
        response.status_code = 500
    else:
        data = res.get("data")

    return api.builder(data, response.status_code)

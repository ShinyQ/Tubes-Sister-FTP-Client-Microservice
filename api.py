def builder(data, code):
    message = "Success"

    if not code:
        code = 200
    elif code == 500:
        message = "Internal Server server"
    elif code == 400:
        message = "Bad Request"
    elif code == 404:
        message = "Not Found"
    elif code == 405:
        message = "Method Not Allowed"

    return {'code': code, 'message': message, 'data': data}

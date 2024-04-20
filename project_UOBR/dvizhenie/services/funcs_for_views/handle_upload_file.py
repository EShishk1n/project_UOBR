def handle_uploaded_file(f):
    """Загружает файл на сервер"""

    with open("dvizhenie/uploads/Движение_БУ.xlsx", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

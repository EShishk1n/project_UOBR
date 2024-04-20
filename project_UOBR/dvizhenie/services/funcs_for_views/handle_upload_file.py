def handle_uploaded_file(f, path: str):
    """Загружает файл на сервер"""

    with open(path, "wb+") as destination:
        print(destination)
        print(f.chunks)
        for chunk in f.chunks():
            print(chunk)
            destination.write(chunk)

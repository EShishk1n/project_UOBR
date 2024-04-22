from django.shortcuts import render


def start_page(request):
    """Рендерит стартовую страницу"""

    return render(request, 'dvizhenie/StaticPages_templates/start_page.html')


def about_app(request):
    """Рендерит страницу 'о приложении'"""

    return render(request, 'dvizhenie/StaticPages_templates/about_app.html')


def contacts(request):
    """Рендерит страницу 'контакты'"""

    return render(request, 'dvizhenie/StaticPages_templates/contacts.html')

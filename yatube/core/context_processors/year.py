import datetime


def year(request):
    """Добавляет переменную с текущим годом.
    Исправил в footer тег.
    """
    return {"year": datetime.datetime.now().year}

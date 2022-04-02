from django.http import HttpResponse


def index(request):
    html = "<html><body><h1>ISCC - Decentralized Content Registry</h1></body></html>"
    return HttpResponse(html)

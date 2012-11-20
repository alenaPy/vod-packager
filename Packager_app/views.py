from django.http import HttpReponse

def index(request):
	return HttpResponse("Hello, world!.")
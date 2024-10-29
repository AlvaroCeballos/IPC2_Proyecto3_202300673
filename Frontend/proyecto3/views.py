from django.shortcuts import render

import requests

def index(request):
    return render(request, 'index.html')

def configurar(request):
    return render(request, 'CargarArchivo.html')

def visualizarXML(request):
    if request.method == 'POST':
        xml_file = request.FILES['file']
        xml_content = xml_file.read().decode('utf-8')
        return render(request, 'CargarArchivo.html', {'xml_content': xml_content})
    return render(request, 'CargarArchivo.html')

def subirXML(request):
    if request.method == 'POST':
        xml_content = request.POST['xml']
        response = requests.post('http://localhost:5000/config/postDiccionarioXML', data=xml_content, headers={'Content-Type': 'text/xml'})
        return render(request, 'CargarArchivo.html', {'response': response.text})
    return render(request, 'CargarArchivo.html')

def generarResultados(request):
    response = requests.get('http://localhost:5000/config/obtenerDiccionario')
    return render(request, 'CargarArchivo.html', {'response': response.text})

# -----------------------------------------------------------------------------------------------------------

def configurar2(request):
    return render(request, 'mensajePrueba.html')

def visualizarXML2(request):
    if request.method == 'POST':
        xml_file = request.FILES['file']
        xml_content = xml_file.read().decode('utf-8')
        return render(request, 'mensajePrueba.html', {'xml_content': xml_content})
    return render(request, 'mensajePrueba.html')

def subirXML2(request):
    if request.method == 'POST':
        xml_content = request.POST['xml']
        response = requests.post('http://localhost:5000/config/postMensajePrueba', data=xml_content, headers={'Content-Type': 'text/xml'})
        return render(request, 'mensajePrueba.html', {'response': response.text})
    return render(request, 'mensajePrueba.html')

def generarResultados2(request):
    response = requests.get('http://localhost:5000/config/obtenerDiccionario')
    return render(request, 'mensajePrueba.html', {'response': response.text})
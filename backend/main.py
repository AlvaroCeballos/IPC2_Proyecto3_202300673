from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from xml.dom.minidom import parseString, Document
import unicodedata


# Flask App
app = Flask(__name__)
CORS(app)



listaDiccionario = []
listaMensajes = []
listaEmpresas = []
listaServicios = []

class diccionario:
    def __init__(self, sentimientosPositivos, sentimientosNegativos, empresasAnalizar):
        self.sentimientosPositivos = sentimientosPositivos
        self.sentimientosNegativos = sentimientosNegativos
        self.empresasAnalizar = empresasAnalizar
class empresa:
    def __init__(self, nombre, servicios):
        self.nombre = nombre
        self.servicios = servicios

class servicio:
    def __init__(self, nombre, alias):
        self.nombre = nombre
        self.descripcion = alias

class mensaje:
    def __init__(self, mensaje):
        self.mensaje = mensaje

def normalize_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove accents
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    return text

@app.route('/hola-mundo', methods=['GET'])
def hola_mundo():
    doc = Document()
    root = doc.createElement("Response")
    doc.appendChild(root)
    
    message = doc.createElement("Message")
    message.appendChild(doc.createTextNode("Hola Mundo"))
    root.appendChild(message)
    
    xml_response = doc.toxml(encoding='utf-8')
    return Response(xml_response, mimetype='application/xml')

@app.route('/config/postDiccionarioXML', methods=['POST'])
def postDiccionarioXML():
    try:
        xml_data = request.data
        dom = parseString(xml_data)
        
        sentimientosPositivosLista = [
            normalize_text(node.firstChild.nodeValue.strip()) 
            for node in dom.getElementsByTagName('sentimientos_positivos')[0].getElementsByTagName('palabra')
        ]
        sentimientosNegativosLista = [
            normalize_text(node.firstChild.nodeValue.strip()) 
            for node in dom.getElementsByTagName('sentimientos_negativos')[0].getElementsByTagName('palabra')
        ]
        
        empresas_analizar = []
        for empresa_node in dom.getElementsByTagName('empresa'):
            nombre = normalize_text(empresa_node.getElementsByTagName('nombre')[0].firstChild.nodeValue.strip())
            servicios = []
            for servicio_node in empresa_node.getElementsByTagName('servicio'):
                nombre_servicio = normalize_text(servicio_node.getAttribute('nombre'))
                alias = [
                    normalize_text(alias_node.firstChild.nodeValue.strip()) 
                    for alias_node in servicio_node.getElementsByTagName('alias')
                ]
                servicios.append(servicio(nombre_servicio, alias))
            empresas_analizar.append(empresa(nombre, servicios))
        
        listaDiccionario.append(diccionario(sentimientosPositivosLista, sentimientosNegativosLista, empresas_analizar))
        
        for mensaje_node in dom.getElementsByTagName('mensaje'):
            mensaje_text = normalize_text(mensaje_node.firstChild.nodeValue.strip())
            listaMensajes.append(mensaje(mensaje_text))
        
        response_doc = Document()
        root = response_doc.createElement("Response")
        response_doc.appendChild(root)
        
        status = response_doc.createElement("Status")
        status.appendChild(response_doc.createTextNode("Success"))
        root.appendChild(status)
        
        xml_response = response_doc.toxml(encoding='utf-8')
        return Response(xml_response, mimetype='application/xml')
    
    except Exception as e:
        response_doc = Document()
        root = response_doc.createElement("Response")
        response_doc.appendChild(root)
        
        status = response_doc.createElement("Status")
        status.appendChild(response_doc.createTextNode("Failure"))
        root.appendChild(status)
        
        error_message = response_doc.createElement("Error")
        error_message.appendChild(response_doc.createTextNode(str(e)))
        root.appendChild(error_message)
        
        xml_response = response_doc.toxml(encoding='utf-8')
        return Response(xml_response, mimetype='application/xml')

@app.route('/config/obtenerDiccionario', methods=['GET'])
def obtenerDiccionario():
    try:
        response_doc = Document()
        root = response_doc.createElement("solicitud_clasificacion")
        response_doc.appendChild(root)
        
        diccionario_element = response_doc.createElement("diccionario")
        root.appendChild(diccionario_element)
        
        for dic in listaDiccionario:
            sentimientos_positivos_element = response_doc.createElement("sentimientos_positivos")
            for palabra in dic.sentimientosPositivos:
                palabra_element = response_doc.createElement("palabra")
                palabra_element.appendChild(response_doc.createTextNode(palabra))
                sentimientos_positivos_element.appendChild(palabra_element)
            diccionario_element.appendChild(sentimientos_positivos_element)
            
            sentimientos_negativos_element = response_doc.createElement("sentimientos_negativos")
            for palabra in dic.sentimientosNegativos:
                palabra_element = response_doc.createElement("palabra")
                palabra_element.appendChild(response_doc.createTextNode(palabra))
                sentimientos_negativos_element.appendChild(palabra_element)
            diccionario_element.appendChild(sentimientos_negativos_element)
            
            empresas_analizar_element = response_doc.createElement("empresas_analizar")
            for emp in dic.empresasAnalizar:
                empresa_element = response_doc.createElement("empresa")
                
                nombre_element = response_doc.createElement("nombre")
                nombre_element.appendChild(response_doc.createTextNode(emp.nombre))
                empresa_element.appendChild(nombre_element)
                
                servicios_element = response_doc.createElement("servicios")
                for serv in emp.servicios:
                    servicio_element = response_doc.createElement("servicio")
                    servicio_element.setAttribute("nombre", serv.nombre)
                    for alias in serv.descripcion:
                        alias_element = response_doc.createElement("alias")
                        alias_element.appendChild(response_doc.createTextNode(alias))
                        servicio_element.appendChild(alias_element)
                    servicios_element.appendChild(servicio_element)
                empresa_element.appendChild(servicios_element)
                
                empresas_analizar_element.appendChild(empresa_element)
            diccionario_element.appendChild(empresas_analizar_element)
        
        lista_mensajes_element = response_doc.createElement("lista_mensajes")
        for msg in listaMensajes:
            mensaje_element = response_doc.createElement("mensaje")
            mensaje_element.appendChild(response_doc.createTextNode(msg.mensaje))
            lista_mensajes_element.appendChild(mensaje_element)
        root.appendChild(lista_mensajes_element)
        
        xml_response = response_doc.toxml(encoding='utf-8')
        return Response(xml_response, mimetype='application/xml')
    
    except Exception as e:
        response_doc = Document()
        root = response_doc.createElement("Response")
        response_doc.appendChild(root)
        
        status = response_doc.createElement("Status")
        status.appendChild(response_doc.createTextNode("Failure"))
        root.appendChild(status)
        
        error_message = response_doc.createElement("Error")
        error_message.appendChild(response_doc.createTextNode(str(e)))
        root.appendChild(error_message)
        
        xml_response = response_doc.toxml(encoding='utf-8')
        return Response(xml_response, mimetype='application/xml')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
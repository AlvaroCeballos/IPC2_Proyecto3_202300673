from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from xml.dom.minidom import parseString, Document
import unicodedata

app = Flask(__name__)
CORS(app)



listaDiccionario = []
listaMensajes = []
listaFechas = []

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

def minuscula(palabraM):
    palabraM = palabraM.lower()
    palabraM = ''.join(
        caracter for caracter in unicodedata.normalize('NFD', palabraM)
        if unicodedata.category(caracter) != 'Mn'
    )
    return palabraM

@app.route('/hola-mundo', methods=['GET'])
def hola_mundo():
    doc = Document()
    nodoRaiz = doc.createElement("HolaMundo")
    doc.appendChild(nodoRaiz)
    message = doc.createElement("hola")
    message.appendChild(doc.createTextNode("Hola Mundo"))
    nodoRaiz.appendChild(message)
    xmlSalida = doc.toxml(encoding='utf-8')
    return Response(xmlSalida, mimetype='application/xml')

@app.route('/config/postDiccionarioXML', methods=['POST'])
def postDiccionarioXML():

    try:
        leerXML = request.data
        documentoXML = parseString(leerXML)
        sentimientosPositivosLista = [minuscula(node.firstChild.nodeValue.strip()) for node in documentoXML.getElementsByTagName('sentimientos_positivos')[0].getElementsByTagName('palabra')]
        sentimientosNegativosLista = [minuscula(node.firstChild.nodeValue.strip()) for node in documentoXML.getElementsByTagName('sentimientos_negativos')[0].getElementsByTagName('palabra')]
        listaEmpresas = []

        for empresaXML in documentoXML.getElementsByTagName('empresa'):
            nombre = minuscula(empresaXML.getElementsByTagName('nombre')[0].firstChild.nodeValue.strip())
            servicios = []

            for servicioXML in empresaXML.getElementsByTagName('servicio'):
                nombreServicioXML = minuscula(servicioXML.getAttribute('nombre'))
                alias = [minuscula(aliasXML.firstChild.nodeValue.strip()) for aliasXML in servicioXML.getElementsByTagName('alias')]
                servicios.append(servicio(nombreServicioXML, alias))
            listaEmpresas.append(empresa(nombre, servicios))
        listaDiccionario.append(diccionario(sentimientosPositivosLista, sentimientosNegativosLista, listaEmpresas))

        for mensajeXML in documentoXML.getElementsByTagName('mensaje'):
            mensajeXML = minuscula(mensajeXML.firstChild.nodeValue.strip())
            listaMensajes.append(mensaje(mensajeXML))
        respuestaFXMLDoc = Document()
        nodoRaiz = respuestaFXMLDoc.createElement("RespuestaEstado")
        respuestaFXMLDoc.appendChild(nodoRaiz)
        estadoActual = respuestaFXMLDoc.createElement("Estado")
        estadoActual.appendChild(respuestaFXMLDoc.createTextNode("XML recibido correctamente"))
        nodoRaiz.appendChild(estadoActual)
        xmlSalida = respuestaFXMLDoc.toxml(encoding='utf-8')

        return Response(xmlSalida, mimetype='application/xml')

    except Exception as e:
        respuestaFXMLDoc = Document()
        nodoRaiz = respuestaFXMLDoc.createElement("RespuestaEstado")
        respuestaFXMLDoc.appendChild(nodoRaiz)
        estadoActual = respuestaFXMLDoc.createElement("Estado")
        estadoActual.appendChild(respuestaFXMLDoc.createTextNode("Algo ha salido muy mal, por favor revisar la esstructura del XML"))
        nodoRaiz.appendChild(estadoActual)
        fatalError = respuestaFXMLDoc.createElement("Error")
        fatalError.appendChild(respuestaFXMLDoc.createTextNode(str(e)))
        nodoRaiz.appendChild(fatalError)
        xmlSalida = respuestaFXMLDoc.toxml(encoding='utf-8')

        return Response(xmlSalida, mimetype='application/xml')

@app.route('/config/obtenerDiccionario', methods=['GET'])
def obtenerDiccionario():

    try:
        respuestaFXMLDoc = Document()
        nodoRaiz = respuestaFXMLDoc.createElement("solicitud_clasificacion")
        respuestaFXMLDoc.appendChild(nodoRaiz)
        diccionarioXMLRE = respuestaFXMLDoc.createElement("diccionario")
        nodoRaiz.appendChild(diccionarioXMLRE)

        for xDiccionario in listaDiccionario:
            sentimientos_positivos_element = respuestaFXMLDoc.createElement("sentimientos_positivos")

            for palabra in xDiccionario.sentimientosPositivos:
                palabraXMLRE = respuestaFXMLDoc.createElement("palabra")
                palabraXMLRE.appendChild(respuestaFXMLDoc.createTextNode(palabra))
                sentimientos_positivos_element.appendChild(palabraXMLRE)
            diccionarioXMLRE.appendChild(sentimientos_positivos_element)
            sentimientos_negativos_element = respuestaFXMLDoc.createElement("sentimientos_negativos")

            for palabra in xDiccionario.sentimientosNegativos:
                palabraXMLRE = respuestaFXMLDoc.createElement("palabra")
                palabraXMLRE.appendChild(respuestaFXMLDoc.createTextNode(palabra))
                sentimientos_negativos_element.appendChild(palabraXMLRE)
            diccionarioXMLRE.appendChild(sentimientos_negativos_element)
            empresasXMLRE = respuestaFXMLDoc.createElement("empresas_analizar")

            for xEmpresa in xDiccionario.empresasAnalizar:
                empresaRE = respuestaFXMLDoc.createElement("empresa")
                nombreEmpresa = respuestaFXMLDoc.createElement("nombre")
                nombreEmpresa.appendChild(respuestaFXMLDoc.createTextNode(xEmpresa.nombre))
                empresaRE.appendChild(nombreEmpresa)
                serviciosRespuestaXML = respuestaFXMLDoc.createElement("servicios")

                for xServicio in xEmpresa.servicios:
                    servicioIndiRes = respuestaFXMLDoc.createElement("servicio")
                    servicioIndiRes.setAttribute("nombre", xServicio.nombre)

                    for alias in xServicio.descripcion:
                        aliasREXML = respuestaFXMLDoc.createElement("alias")
                        aliasREXML.appendChild(respuestaFXMLDoc.createTextNode(alias))
                        servicioIndiRes.appendChild(aliasREXML)
                    serviciosRespuestaXML.appendChild(servicioIndiRes)
                empresaRE.appendChild(serviciosRespuestaXML)
                empresasXMLRE.appendChild(empresaRE)
            diccionarioXMLRE.appendChild(empresasXMLRE)
        LMensajesXML = respuestaFXMLDoc.createElement("lista_mensajes")

        for xMensaje in listaMensajes:
            mensajeSalidaXMLR = respuestaFXMLDoc.createElement("mensaje")
            mensajeSalidaXMLR.appendChild(respuestaFXMLDoc.createTextNode(xMensaje.mensaje))
            LMensajesXML.appendChild(mensajeSalidaXMLR)
        nodoRaiz.appendChild(LMensajesXML)
        xmlSalida = respuestaFXMLDoc.toxml(encoding='utf-8')

        return Response(xmlSalida, mimetype='application/xml')

    except Exception as e:
        respuestaFXMLDoc = Document()
        nodoRaiz = respuestaFXMLDoc.createElement("Validacion")
        respuestaFXMLDoc.appendChild(nodoRaiz)
        estadoActual = respuestaFXMLDoc.createElement("Estado")
        estadoActual.appendChild(respuestaFXMLDoc.createTextNode("ha ocurrido un error muy grave, por favor revisar la estructura del XML"))
        nodoRaiz.appendChild(estadoActual)
        fatalError = respuestaFXMLDoc.createElement("Error")
        fatalError.appendChild(respuestaFXMLDoc.createTextNode(str(e)))
        nodoRaiz.appendChild(fatalError)
        xmlSalida = respuestaFXMLDoc.toxml(encoding='utf-8')
        return Response(xmlSalida, mimetype='application/xml')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
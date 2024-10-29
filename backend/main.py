import re
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from xml.dom.minidom import parseString, Document
import unicodedata

app = Flask(__name__)
CORS(app)



listaDiccionario = []
listaMensajes = []
listaFechas = []
listaMensajePrueba = []
sentimientosPositivosLista = []
sentimientosNegativosLista = []

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

class fecha:
    def __init__(self, fecha):
        self.fecha = fecha

def minuscula(palabraM):
    palabraM = palabraM.lower()
    palabraM = ''.join(
        caracter for caracter in unicodedata.normalize('NFD', palabraM)
        if unicodedata.category(caracter) != 'Mn'
    )
    return palabraM

@app.route('/holaMundo', methods=['GET'])
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
    global sentimientosPositivosLista
    global sentimientosNegativosLista

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

#--------------------------------------------------------------------------------RESPUESTA SOLIDA DE LA APLICACION---------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/config/postDiccionarioMedioProcesado', methods=['POST'])
def postDiccionarioXMLMedioProcesado():
    global sentimientosPositivosLista
    global sentimientosNegativosLista

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

@app.route('/config/obtenerDiccionarioMedioProcesado', methods=['GET'])
def obtenerDiccionarioMedioProcesado():

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
#--------------------------------------------------------------------------------FIN SOLIDO---------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
@app.route('/config/postMensajePrueba', methods=['POST'])
def postMensajePrueba():
    try:
        leerXML = request.data
        documentoXML = parseString(leerXML)
        
        # Extract and normalize the message content
        mensajeXML = documentoXML.getElementsByTagName('mensaje')[0].firstChild.nodeValue.strip()
        mensajeNormalizado = minuscula(mensajeXML)
        
        # Extract additional information
        fechaRespuesta = re.search(r'(\d{2}/\d{2}/\d{4})', mensajeNormalizado).group(1)
        usuarioRespuesta = re.search(r'usuario: ([^\s]+)', mensajeNormalizado).group(1)
        redSocial = re.search(r'red social: ([^\s]+)', mensajeNormalizado).group(1)
        
        # Analyze sentiment
        palabras = re.findall(r'\b\w+\b', mensajeNormalizado.lower())
        contador_positivas = sum(1 for palabra in palabras if palabra in sentimientosPositivosLista)
        contador_negativas = sum(1 for palabra in palabras if palabra in sentimientosNegativosLista)
        
        total_palabras = contador_positivas + contador_negativas
        sentimiento_positivo = (contador_positivas / total_palabras * 100) if total_palabras > 0 else 0
        sentimiento_negativo = (contador_negativas / total_palabras * 100) if total_palabras > 0 else 0
        
        sentimiento_analizado = "neutro"
        if sentimiento_positivo > sentimiento_negativo:
            sentimiento_analizado = 'positivo'
        elif sentimiento_positivo < sentimiento_negativo:
            sentimiento_analizado = 'negativo'
        
        # Create response XML
        respuestaFXMLDoc = Document()
        nodoRaiz = respuestaFXMLDoc.createElement("respuesta")
        respuestaFXMLDoc.appendChild(nodoRaiz)
        
        fecha_element = respuestaFXMLDoc.createElement("fecha")
        fecha_element.appendChild(respuestaFXMLDoc.createTextNode(fechaRespuesta))
        nodoRaiz.appendChild(fecha_element)
        
        red_social_element = respuestaFXMLDoc.createElement("red_social")
        red_social_element.appendChild(respuestaFXMLDoc.createTextNode(redSocial))
        nodoRaiz.appendChild(red_social_element)
        
        usuario_element = respuestaFXMLDoc.createElement("usuario")
        usuario_element.appendChild(respuestaFXMLDoc.createTextNode(usuarioRespuesta))
        nodoRaiz.appendChild(usuario_element)
        
        empresas_element = respuestaFXMLDoc.createElement("empresas")
        empresa_element = respuestaFXMLDoc.createElement("empresa")
        empresa_element.setAttribute("nombre", "USAC")
        servicio_element = respuestaFXMLDoc.createElement("servicio")
        servicio_element.appendChild(respuestaFXMLDoc.createTextNode("inscripción"))
        empresa_element.appendChild(servicio_element)
        empresas_element.appendChild(empresa_element)
        nodoRaiz.appendChild(empresas_element)
        
        palabras_positivas_element = respuestaFXMLDoc.createElement("palabras_positivas")
        palabras_positivas_element.appendChild(respuestaFXMLDoc.createTextNode(str(contador_positivas)))
        nodoRaiz.appendChild(palabras_positivas_element)
        
        palabras_negativas_element = respuestaFXMLDoc.createElement("palabras_negativas")
        palabras_negativas_element.appendChild(respuestaFXMLDoc.createTextNode(str(contador_negativas)))
        nodoRaiz.appendChild(palabras_negativas_element)
        
        sentimiento_positivo_element = respuestaFXMLDoc.createElement("sentimiento_positivo")
        sentimiento_positivo_element.appendChild(respuestaFXMLDoc.createTextNode(f"{sentimiento_positivo:.2f}%"))
        nodoRaiz.appendChild(sentimiento_positivo_element)
        
        sentimiento_negativo_element = respuestaFXMLDoc.createElement("sentimiento_negativo")
        sentimiento_negativo_element.appendChild(respuestaFXMLDoc.createTextNode(f"{sentimiento_negativo:.2f}%"))
        nodoRaiz.appendChild(sentimiento_negativo_element)
        
        sentimiento_analizado_element = respuestaFXMLDoc.createElement("sentimiento_analizado")
        sentimiento_analizado_element.appendChild(respuestaFXMLDoc.createTextNode(sentimiento_analizado))
        nodoRaiz.appendChild(sentimiento_analizado_element)
        
        xmlSalida = respuestaFXMLDoc.toxml(encoding='utf-8')
        return Response(xmlSalida, mimetype='application/xml')
    
    except Exception as e:
        respuestaFXMLDoc = Document()
        nodoRaiz = respuestaFXMLDoc.createElement("RespuestaEstado")
        respuestaFXMLDoc.appendChild(nodoRaiz)
        
        estadoActual = respuestaFXMLDoc.createElement("Estado")
        estadoActual.appendChild(respuestaFXMLDoc.createTextNode("Algo ha salido muy mal, por favor revisar la estructura del XML"))
        nodoRaiz.appendChild(estadoActual)
        
        fatalError = respuestaFXMLDoc.createElement("Error")
        fatalError.appendChild(respuestaFXMLDoc.createTextNode(str(e)))
        nodoRaiz.appendChild(fatalError)
        
        xmlSalida = respuestaFXMLDoc.toxml(encoding='utf-8')
        return Response(xmlSalida, mimetype='application/xml')
    

#Ahora los mensajes del apartado de prueba
if __name__ == '__main__':
    app.run(debug=True, port=5000)
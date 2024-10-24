from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from xml.dom.minidom import parseString, Document
import diccionario

# Flask App
app = Flask(__name__)
CORS(app)



listaDiccionario = []

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
    data = request.get_data().decode('utf-8').strip()
    dom = parseString(data)
    
    sentimientos_positivos = [palabra.firstChild.nodeValue.strip() for palabra in dom.getElementsByTagName('sentimientos_positivos')[0].getElementsByTagName('palabra')]
    sentimientos_negativos = [palabra.firstChild.nodeValue.strip() for palabra in dom.getElementsByTagName('sentimientos_negativos')[0].getElementsByTagName('palabra')]
    
    empresas = dom.getElementsByTagName('empresa')
    empresas_analizar = []
    for empresa in empresas:
        nombre = empresa.getElementsByTagName('nombre')[0].firstChild.nodeValue.strip()
        servicios = empresa.getElementsByTagName('servicio')
        servicios_dict = {}
        for servicio in servicios:
            servicio_nombre = servicio.getAttribute('nombre').strip()
            alias_list = [alias.firstChild.nodeValue.strip() for alias in servicio.getElementsByTagName('alias')]
            servicios_dict[servicio_nombre] = alias_list
        empresas_analizar.append({'nombre': nombre, 'servicios': servicios_dict})
    
    nuevo_diccionario = diccionario.Diccionario(sentimientos_positivos, sentimientos_negativos, empresas_analizar)
    listaDiccionario.append(nuevo_diccionario)
    
    doc = Document()
    root = doc.createElement("Response")
    doc.appendChild(root)
    message = doc.createElement("Message")
    message.appendChild(doc.createTextNode("XML de diccionario recibido"))
    root.appendChild(message)
    
    xml_response = doc.toxml(encoding='utf-8')
    return Response(xml_response, mimetype='application/xml')

@app.route('/config/obtenerDiccionario', methods=['GET'])
def obtenerDiccionario():
    if not listaDiccionario:
        return Response("<Response><Message>No hay diccionarios almacenados</Message></Response>", mimetype='application/xml')
    
    diccionario_obj = listaDiccionario[-1]
    
    doc = Document()
    root = doc.createElement("diccionario")
    doc.appendChild(root)
    
    sentimientos_positivos_elem = doc.createElement("sentimientos_positivos")
    for palabra in diccionario_obj.sentimientosPositivos:
        palabra_elem = doc.createElement("palabra")
        palabra_elem.appendChild(doc.createTextNode(palabra))
        sentimientos_positivos_elem.appendChild(palabra_elem)
    root.appendChild(sentimientos_positivos_elem)
    
    sentimientos_negativos_elem = doc.createElement("sentimientos_negativos")
    for palabra in diccionario_obj.sentimientosNegativos:
        palabra_elem = doc.createElement("palabra")
        palabra_elem.appendChild(doc.createTextNode(palabra))
        sentimientos_negativos_elem.appendChild(palabra_elem)
    root.appendChild(sentimientos_negativos_elem)
    
    empresas_analizar_elem = doc.createElement("empresas_analizar")
    for empresa in diccionario_obj.empresasAnalizar:
        empresa_elem = doc.createElement("empresa")
        
        nombre_elem = doc.createElement("nombre")
        nombre_elem.appendChild(doc.createTextNode(empresa['nombre']))
        empresa_elem.appendChild(nombre_elem)
        
        servicios_elem = doc.createElement("servicios")
        for servicio_nombre, alias_list in empresa['servicios'].items():
            servicio_elem = doc.createElement("servicio")
            servicio_elem.setAttribute("nombre", servicio_nombre)
            for alias in alias_list:
                alias_elem = doc.createElement("alias")
                alias_elem.appendChild(doc.createTextNode(alias))
                servicio_elem.appendChild(alias_elem)
            servicios_elem.appendChild(servicio_elem)
        empresa_elem.appendChild(servicios_elem)
        
        empresas_analizar_elem.appendChild(empresa_elem)
    root.appendChild(empresas_analizar_elem)
    
    xml_response = doc.toxml(encoding='utf-8')
    return Response(xml_response, mimetype='application/xml')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
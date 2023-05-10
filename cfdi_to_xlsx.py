# script header
# Author:           [Hugo Berra Salazar, ]
# Creation date:    [04/24/2023]
# Description:      [Brief description of the purpose of the script]

# import necessary modules
import os
import pandas as pd
import json

from lxml           import etree
from datetime           import datetime, timedelta

# Gets the current date and time
now = datetime.now().strftime('%m%d%Y-%H%M%S')

def get_dir_path_data(option, rfc):
    dirs = {
        'AYUDAS'        : f'{rfc}/Emisor/Ayudas/',
        'INGRESO'       : f'{rfc}/Emisor/Ingresos/',
        'NOMINA'        : f'{rfc}/Emisor/Nomina/',
        'PAGO_E'        : f'{rfc}/Emisor/Pagos/',
        'DES_BON_DEV'   : f'{rfc}/Receptor/Descuento_Bonificaciones_Devoluciones/',
        'GASTO'         : f'{rfc}/Receptor/Gastos/',
        'PAGO_R'        : f'{rfc}/Receptor/Pagos/'
    }
    return dirs.get(option)

def type_receipt_with_letter(type_recipt):
    type_recipt_list = {
        'I':'Ingreso',
        'N':'Nomina',
        'E':'Egreso',
        'P':'Pago'
    }
    return type_recipt_list.get(type_recipt)

def add_row(nodo, fila):
    # Add "cfdi:Comprobante" node as new column
    if nodo.tag.endswith('Comprobante'):
        fila['Serie']            = nodo.attrib.get('Serie'              , "-")
        fila['Folio']            = nodo.attrib.get('Folio'              , "-")
        fila['Subtotal']         = nodo.attrib.get('SubTotal'           , "-")
        fila['Descuento']        = nodo.attrib.get('Descuento'          , "-")
        fila['Tipo de Cambio']   = nodo.attrib.get('TipoCambio'         , "-")
        fila['Version']          = nodo.attrib.get('Version'            , "-")
        fila['Fecha Emision']    = nodo.attrib.get('Fecha'              , "-")
        fila['Tipo Comprobante'] = nodo.attrib.get('TipoDeComprobante'  , "-")
        fila['Subtotal']         = nodo.attrib.get('SubTotal'           , "-")
        fila['Total']            = nodo.attrib.get('Total'              , "-")
        fila['Moneda']           = nodo.attrib.get('Moneda'             , "-")
        fila['CP Emisor']        = nodo.attrib.get('LugarExpedicion'    , "-")
        fila['Moneda']           = nodo.attrib.get('Moneda'             , "-")
        fila['Metodo Pago']      = nodo.attrib.get('MetodoPago'         , "-")
        fila['Forma Pago']       = nodo.attrib.get('FormaPago'          , "-")
        fila['Tipo']             = type_receipt_with_letter(fila['TipoDeComprobante'])

    # Add "cfdi:Emisor" attribs as new row
    if nodo.tag.endswith('CfdiRelacionados'):
        fila['Tipo Relacion']    = nodo.attrib.get('TipoRelacion', "-")
        
    if nodo.tag.endswith('Emisor'):
        fila['RFC Emisor']       = nodo.attrib.get('Rfc'    , "-")
        fila['Nombre Emisor']    = nodo.attrib.get('Nombre' , "-")

    # Add "cfdi:Receptor" attribs as new row
    if nodo.tag.endswith('Receptor'):
        fila['RFC Receptor']    = nodo.attrib.get('Rfc'     , "-")
        fila['Nombre Receptor'] = nodo.attrib.get('Nombre'  , "-")

    if nodo.tag.endswith('Conceptos'):
        # Create an empty dictionary to store the concept data
        lista_conceptos = []

        conceptos = nodo.xpath('//cfdi:Conceptos/cfdi:Concepto', namespaces=nodo.nsmap)
        # Iterate over the cfdi:Concept elements and add their data to the dictionary
        for concepto in conceptos:
            datos_concepto = {
                "ClaveProdServ"     : concepto.get("ClaveProdServ"   , "-"),
                "NoIdentificacion"  : concepto.get("NoIdentificacion", "-"),
                "Cantidad"          : concepto.get("Cantidad"        , "-"),
                "Clave Unidad"      : concepto.get("ClaveUnidad"     , "-"),
                "Unidad"            : concepto.get("Unidad"          , "-"),
                "Descripcion"       : concepto.get("Descripcion"     , "-"),
                "Valor Unitario"    : concepto.get("ValorUnitario"   , "-"),
                "Importe"           : concepto.get("Importe"         , "-"),
                "Descuento"         : concepto.get("Descuento"       , "-")
            }
            lista_conceptos.append(datos_concepto)
        # Add the list of concepts to the main dictionary
        fila["Lista de Conceptos"] = json.dumps(lista_conceptos)
    
    # Add "cfdi:TimbreFiscalDigital" attribs as new row
    if nodo.tag.endswith('TimbreFiscalDigital'):
        fila['Fecha Timbrado']  = nodo.attrib['FechaTimbrado']
        fila['UUID']            = nodo.attrib['UUID']
    
    return fila

def cfdi_to_dict(option, rfc):
    # Define the path of cfdi's dir 
    dirpath     = get_dir_path_data(option, rfc)
    
    filas       = []

    try:
        # Iterate over all XML files in the specified path
        for dir, subdir, files in os.walk(dirpath):
            for file in files:
                if file.endswith(".xml"):
                    # Get the full path of the XML file
                    filename = os.path.join(dir, file)
                
                    # Parse the XML file with lxml
                    try: 
                        arbol = etree.parse(filename)
                    except:
                        raise Exception(f'E1: Impossible to parse the tree: {filename}')
                    
                    # Create a columns for the current file
                    try:
                        if option == "NOMINA":
                            with open('payroll-columns.json', encoding='utf-8') as f:
                                fila = json.load(f)
                        else:
                            with open('cfdi-colums.json', encoding='utf-8') as f:
                                fila = json.load(f)        
                    except:
                        raise Exception(f'E2: Impossible to get xlsx columns: {option}')
                    
                    # Get all attribute values for each node in the file
                    for nodo in arbol.iter():
                        fila = add_row(nodo, fila)
                                
                    # creates a list of the concepts and inserts them in the column "List of Concepts"
                    #conceptos = get_concepts(filename)
                    #fila['Lista de Conceptos'] = str(conceptos)

                    # Add the row to the list of rows
                    filas.append(fila)
                    
                    # break # eliminame para iterar en todos lo CFDI (ahora solo hay uno para pruebas)

    except Exception as e:
        print(f'{e}')
        pass

    return filas, dirpath

def dict_to_xlsx(option, rfc):

    filas, dirpath = cfdi_to_dict(option, rfc)
    
    # print (filas)
    # return # eliminame para crear el xlsx (ahora solo imprime en consola)
    
    try:
        # Create a DataFrame from the list of rows
        df = pd.concat([pd.DataFrame(fila, index=[0]) for fila in filas], ignore_index=True)

        # Create a ExcelWriter object
        writer = pd.ExcelWriter(f"{dirpath}/{now}-{option}.xlsx", engine='xlsxwriter')

        # Define the formatting for the header row
        header_format = writer.book.add_format({'bold': True, 'bg_color': '#730707', 'font_color': 'white'})

        # Convert the DataFrame to an Excel sheet
        df.to_excel(writer, sheet_name=f'{option}', index=False)
        
        worksheet = writer.sheets[f'{option}']

        # Format the header row
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # # Set the column widths to auto-fit
        # for i, col in enumerate(df.columns):
        #     column_width = max(df[col].astype(str).map(len).max(), len(col))
        #     worksheet.set_column(i, i, column_width)

        # Save the Excel file
        writer.close()
    except Exception as e:
        print(f'E2: {e}')
        pass

# Main script code
if __name__ == '__main__':
    # Code that is executed when the script is called directly
    # DES_BON_DEV, INGRESO
    dict_to_xlsx('INGRESO', 'MAP850101324')
    pass
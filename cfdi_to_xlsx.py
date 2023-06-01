# script header
# Author:           [Hugo Berra Salazar, ]
# Creation date:    [04/24/2023]
# Description:      [Brief description of the purpose of the script]

# import necessary modules
import os
import pandas as pd
import json

from lxml               import etree
from datetime           import datetime
from cfdi_row           import cfdi_row 
from cfdi_payroll_row   import cfdi_payroll_row

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

def set_json_template(option):
    # calls the specific path of the json
    dirs = {
        'AYUDAS'        : '',
        'INGRESO'       : '',
        'NOMINA'        : '',
        'PAGO_E'        : '',
        'DES_BON_DEV'   : '',
        'GASTO'         : '',
        'PAGO_R'        : ''
    }
    return dirs.get(option)

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
                        with open(set_json_template(option), encoding='utf-8') as f:
                            fila = json.load(f)

                        for nodo in arbol.iter():
                            try:
                                fila = cfdi_row(nodo, fila, filename, option, rfc)
                            except:
                                raise Exception(f'E2: an error occurred filling the dictionary {filename}')                
                    except:
                        raise Exception(f'E3: Impossible to get xlsx columns: {filename}')
                    
                    # Get all attribute values for each node in the file
                    fila['Archivo XML'] = filename

                    # Add the row to the list of rows
                    filas.append(fila)

        return filas, dirpath
    
    except Exception as e:
        print(f'cfdi_to_dict E: {e}')
        pass

def dict_to_xlsx(option, rfc):
    try:
        filas, dirpath = cfdi_to_dict(option, rfc)

        # Create a DataFrame from the list of rows
        df = pd.concat([pd.DataFrame(fila, index=[0]) for fila in filas], ignore_index=True)

        # Create a ExcelWriter object
        writer = pd.ExcelWriter(f"{dirpath}/{option}-{datetime.now().strftime('%m%d%Y-%H%M%S')}.xlsx", engine='xlsxwriter')

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
        print(f'E4: {e}')
        pass
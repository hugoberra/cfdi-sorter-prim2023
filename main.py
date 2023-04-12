#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-

# script header
# Author:           [Hugo Berra Salazar, ]
# Creation date:    [04/07/2023]
# Description:      [Brief description of the purpose of the script]

# import necessary modules
import os
from cfdi_sorter import cfdi_sorter
from prueba import cfdi_to_xlsx

# Function to clear the console screen
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def select_type_report(rfc, dir):
    
    options = {'1': 'ayudas', '2': 'ingreso', '3': 'gasto', '4': 'des_bon_dev', '5': 'gasto', '6': 'pagos'}

    while True:
        #clear()
        print("Menu [3] Select a type report:")
        print('Select an option:')
        print('1. report in excel for receipt type help')
        print('2. report in excel for receipt type income')
        print('3. report in excel for receipt type issuer/expense')
        print('4. report in excel for receipt type discounts bonuses returns')
        print('5. report in excel for receipt type receiver/expense')
        print('6. report in excel for receipt type pay')
        print('7. Return to previous menu')
    
        opcion = input("\nSelect an option: ")

        if options.get(opcion):
            cfdi_to_xlsx(rfc, options.get(opcion), dir)
        elif opcion == '7':
            break
        else:
            input('Invalid option. Press Enter to try again...')

# Function to display the municipalities menu
def select_municipality():
    while True:
        clear()
        print("Menu [1] Select a municipality:")
        print("1. MAP: MAP850101324")
        print("2. MCM: MCM8501012U0")
        print("3. MHS: MHS850101F67")
        print("4. MOP: MOP850101NX1")
        print("5. MTR: MTR9302155L8")
        print("0. Exit")
        opcion = input("\nSelect an option: ")
        if opcion   == '1':
            select_algorithm('MAP850101324')
        elif opcion == '2':
            select_algorithm('MCM8501012U0')
        elif opcion == '3':
            select_algorithm('MHS850101F67')
        elif opcion == '4':
            select_algorithm('MOP850101NX1')
        elif opcion == '5':
            select_algorithm('MTR9302155L8')
        elif opcion == '0':
            break
        else:
            input('Invalid option. Press Enter to try again...')

# Function to show algorithms menu
def select_algorithm(rfc):
    while True:
        clear()
        print("Menu [2] Select:")
        print("1. Sort the xml by type of receipt and methot of payment")
        print("2. Create report Excel (xlsx)")
        print("3. Create files pdf (xml to pdf)")
        print("4. Return to previous menu")
        opcion = input("\nSelect an option: ")
        if opcion == '1':
            print("Option 1 selected")
            #cfdi_sorter(rfc, 'Clientes/' + rfc[0:3] + '/')
            """ 
                XML DE PRUEBA 
            """
            cfdi_sorter(rfc, 'xml_new_data')
            
            input("Press Enter to return to the main menu...")
            break
        elif opcion == '2':
            print("Option 2 selected")
            select_type_report(rfc, 'xml_new_data')
            input("Press Enter to return to the main menu...")
            break
        elif opcion == '3':
            print("Option 3 selected")
            input("Press Enter to return to the main menu...")
            break
        elif opcion == '4':
            break
        else:
            input('Invalid option. Press Enter to try again...')

# Código principal del script
if __name__ == '__main__':
    # Código que se ejecuta cuando el script se llama directamente
    select_municipality()
    pass

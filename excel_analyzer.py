from curses import keyname
from itertools import count
from multiprocessing.connection import wait
from multiprocessing.sharedctypes import Value
from pickle import FALSE
from re import T
from time import sleep
from typing import Counter
from joblib import PrintTime
from numpy import where
from openpyxl import load_workbook
import pandas as pd
from IPython.display import display
import pprint as pp

from tqdm import tnrange 

mi_excel = pd.read_excel('Excel_Uvieta.xlsx', sheet_name=1, engine='openpyxl') #Selecciona la hoja de cálculo a utilizar

mis_vocablos = mi_excel['Lema'].tolist() #Guarda todos los vocablos en una lista de python
mis_categorias = mi_excel['Categoría'].tolist() #Guarda todos los vocablos en una lista de python

# Creamos lista de vocablos únicos
vocablos_unicos = list(dict.fromkeys(mis_vocablos)) # Recordar que los diccionarios en Python no admiten duplicados

#Cuenta la ocurrencia de cada vocablo en el texto
mis_numeros = {}

for lema in vocablos_unicos:
    counter = mis_vocablos.count(lema)
    mis_numeros[lema] = counter

mis_resultados = pd.DataFrame.from_dict(mis_numeros, orient='index').reset_index() #Inserta el resultado en un dataframe
mis_resultados.columns=['Lema','Ocurrencia']

#Cuenta categorías

cuenta_categorias = {}
categorias = list(dict.fromkeys(mis_categorias)) #Lista de nuestras categorías

for cat in mis_categorias:
    counter = mis_categorias.count(cat)
    cuenta_categorias[cat] = counter

#Cuenta ocurrencia de vocablo en una categoría

mis_ocurrencias = {}

for lema in mis_vocablos:
    mis_indices = []
    mis_ocurrencias[lema]= {}  

    for index in range(len(mis_vocablos)):
        if mis_vocablos[index] == lema:
            mis_indices.append(index)
    for i in mis_indices:
        cat_lema = mis_categorias[i]

        if cat_lema in mis_ocurrencias[lema]:
            mis_ocurrencias[lema][cat_lema] += 1 

        else:
            mis_ocurrencias[lema][cat_lema] = 1 



mis_columnas = [['LEMA', 'NOUN', 'ADJECTIVE', 'VERB', 'ADVERB', 'PRONOUN', 'PREPOSITION', 'CONJUNCTION', 'INTERJECTION', 'DETERMINER']]
                   

for key in mis_ocurrencias:
    lista_lemas = [key, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for cat in mis_ocurrencias[key]:
        if cat == 'N':
            lista_lemas[1] = mis_ocurrencias[key][cat]
        elif cat == 'A':
            lista_lemas[2] = mis_ocurrencias[key][cat] 
        elif cat == 'V':
            lista_lemas[3] = mis_ocurrencias[key][cat]  
        elif cat == 'ADV':
            lista_lemas[4] = mis_ocurrencias[key][cat]          
        elif cat == 'PRON':
            lista_lemas[5] = mis_ocurrencias[key][cat]
        elif cat == 'P':
            lista_lemas[6] = mis_ocurrencias[key][cat]
        elif cat == 'CONJ':
            lista_lemas[7] = mis_ocurrencias[key][cat]
        elif cat == 'INTER':
            lista_lemas[8] = mis_ocurrencias[key][cat]
        elif cat == 'D':
            lista_lemas[9] = mis_ocurrencias[key][cat]
    mis_columnas.append(lista_lemas)




df = pd.DataFrame(mis_columnas)
# book = load_workbook('Excel_Uvieta.xlsx')
# writer = pd.ExcelWriter('Excel_Uvieta.xlsx', engine='openpyxl')
# writer.book = book
# df.to_excel(writer, sheet_name='HMM', index=False, header=0)
# writer.save()
# writer.close()

mi_HMM = pd.read_excel('Excel_Uvieta.xlsx', sheet_name='HMM', engine='openpyxl') #Selecciona la hoja de cálculo a utilizar

for column in mi_HMM:
    if column == 'NOUN':
        mi_HMM['NOUN'] = mi_HMM['NOUN'] / cuenta_categorias['N']
    elif column == 'ADJECTIVE':
        mi_HMM['ADJECTIVE'] = mi_HMM['ADJECTIVE'] / cuenta_categorias['A']
    elif column == 'VERB':
        mi_HMM['VERB'] = mi_HMM['VERB'] / cuenta_categorias['V']  
    elif column == 'ADVERB':
        mi_HMM['ADVERB'] = mi_HMM['ADVERB'] / cuenta_categorias['ADV']
    elif column == 'PRONOUN':
        mi_HMM['PRONOUN'] = mi_HMM['PRONOUN'] / cuenta_categorias['PRON']
    elif column == 'PREPOSITION':
        mi_HMM['PREPOSITION'] = mi_HMM['PREPOSITION'] / cuenta_categorias['P']
    elif column == 'CONJUNCTION':
        mi_HMM['CONJUNCTION'] = mi_HMM['CONJUNCTION'] / cuenta_categorias['CONJ']
    elif column == 'INTERJECTION':
        mi_HMM['INTERJECTION'] = mi_HMM['INTERJECTION'] / cuenta_categorias['INTER']
    elif column == 'DETERMINER':
        mi_HMM['DETERMINER'] = mi_HMM['DETERMINER'] / cuenta_categorias['D']

# print(mi_HMM)
# book = load_workbook('Excel_Uvieta.xlsx')
# writer = pd.ExcelWriter('Excel_Uvieta.xlsx', engine='openpyxl')
# writer.book = book
# mi_HMM.to_excel(writer, sheet_name='HMM Probabilities', index=False)
# writer.save()
# writer.close()

# ------------ Inicio y final ------------------#


# ------------ Calcular trans ------------------#

mis_trans = dict(Counter(zip(mis_categorias[:-1],mis_categorias[1:]))) #Trancisiones 
trans_xlx = dict.fromkeys(categorias, 0)
trans_list = list(mis_trans.keys())
trans_list_values = list(mis_trans.values())


#Crea diccionario vacío
for key in trans_xlx:
    trans_xlx[key] = dict.fromkeys(categorias, 0)
# print(trans_xlx)


# ------------ Llena diccinario según la data ------------------#
for key in trans_xlx:
    print(f"Mi key es: {key}")
    for trans in trans_list:
        i = trans_list.index(trans)
        if key == trans[0]:
            print(f'Mi trans es: {trans}')
            mi_cat_temp = trans[0]
            trans_temp = trans[1]
            mi_trans_value = trans_list_values[i]
            # print(f'{mi_cat_temp} es seguida de {trans_temp} {trans_list_values[i]} veces')
            trans_xlx[key][trans_temp] = mi_trans_value
print(trans_xlx)

#-------------------Pasamos nuestras transiciones a dataframe y a excel ---------------------------------------#

trans_df = pd.DataFrame(trans_xlx) #Pasamos a dataframe
display(trans_df.transpose())
print(cuenta_categorias)
for column in trans_df:
    # print (f"Mi columna es {column}")
    mi_columna = column
    for cat in cuenta_categorias:
        # print(f'Mi categoría es {cat}')
        if column == cat:
           trans_df[column] = trans_df[column] / cuenta_categorias[cat]

trans_df = trans_df.transpose()
print('Pasando a excel...')
book = load_workbook('Excel_Uvieta.xlsx')
writer = pd.ExcelWriter('Excel_Uvieta.xlsx', engine='openpyxl')
writer.book = book
trans_df.to_excel(writer, sheet_name='Probabilidades Trans')
writer.save()
writer.close()
print("Excel listo 🥳")



















# Añade todos nuestros resultados al Excel
# book = load_workbook('Excel_Uvieta.xlsx')
# writer = pd.ExcelWriter('Excel_Uvieta.xlsx', engine='openpyxl')
# writer.book = book
# mis_resultados.to_excel(writer, sheet_name='Resultados',index=False)
# writer.save()
# writer.close()

# print("Excel listo 🥳")

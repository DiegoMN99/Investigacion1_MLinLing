from concurrent.futures.process import _ThreadWakeup
from curses import keyname
from itertools import count
from multiprocessing.connection import wait
from multiprocessing.sharedctypes import Value
from pickle import FALSE
from re import T
from time import sleep
from typing import Counter
from joblib import PrintTime
from numpy import true_divide, where
from openpyxl import load_workbook
import pandas as pd
from IPython.display import display
import pprint as pp
import re   # Carga  el paquete de las expresiones regulares
import string
from tqdm import tnrange 

# ----------------------------------------- Variables iniciales ----------------------------------------------------#

mi_excel = pd.read_excel('Excel_Uvieta.xlsx', sheet_name=1, engine='openpyxl') #Selecciona la hoja de cálculo a utilizar
mis_vocablos = mi_excel['Lema'].tolist() #Guarda todos los vocablos en una lista de python
mis_categorias = mi_excel['Categoría'].tolist() #Guarda todas las categorías en una lista de python

# ------ Crea nuevas pestañas en nuestra hoja de calculo, basado en un dataframe de pandas que crearemos más adelante --------#

def send_to_excel_sheet(df, sheet_name=''):
    
    print('Pasando a excel...')
    book = load_workbook('Excel_Uvieta.xlsx')
    writer = pd.ExcelWriter('Excel_Uvieta.xlsx', engine='openpyxl')
    writer.book = book
    df.to_excel(writer, sheet_name='Probabilidades Trans')
    writer.save()
    writer.close()
    print("Excel listo 🥳")

# ----------------------------------------- Creamos lista de vocablos únicos ----------------------------------------------------#

vocablos_unicos = list(dict.fromkeys(mis_vocablos)) # Recordar que los diccionarios en Python no admiten duplicados

# ----------------------------------------- Cuenta la ocurrencia de cada vocablo en el texto -----------------------------------#

mis_numeros = {}

for lema in vocablos_unicos:            
    counter = mis_vocablos.count(lema)  #Itera a través de cada categoría y cuenta su ocurrencia
    mis_numeros[lema] = counter

mis_resultados = pd.DataFrame.from_dict(mis_numeros, orient='index').reset_index() #Inserta el resultado en un dataframe
mis_resultados.columns=['Lema','Ocurrencia']

send_to_excel_sheet(mis_resultados, sheet_name='Ocurrencia por vocablo') #Enviamos el dataframe a nuestro excel

# --------------------------------------- Cuenta la ocurrencia de cada categoría en el texto -----------------------------------#

cuenta_categorias = {}
categorias = list(dict.fromkeys(mis_categorias)) #Lista de nuestras categorías

for cat in mis_categorias:
    counter = mis_categorias.count(cat)
    cuenta_categorias[cat] = counter

# --------------------------------- Cuenta la ocurrencia de cada palabra en cada categoria --------------------------------#

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


# --------------------------------- Arma la matriz para visualizar los resultados --------------------------------#


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

df = pd.DataFrame(mis_columnas) #Convertimos la matriz a dataframe
send_to_excel_sheet(df, sheet_name='HMM', index=False, header=0) #Enviamos el dataframe a nuestro excel

# --------------------------------- Calculamos las frecuencias por vocablo --------------------------------#

mi_HMM = pd.read_excel('Excel_Uvieta.xlsx', sheet_name='HMM', engine='openpyxl') #Selecciona la hoja de cálculo a utilizar

for column in mi_HMM:
    if column == 'NOUN':
        mi_HMM['NOUN'] = mi_HMM['NOUN'] / cuenta_categorias['N'] #Dividimos ocurrencias entre total de emisiones
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

send_to_excel_sheet(mi_HMM, sheet_name='HMM Probabilities') #Enviamos el dataframe a nuestro excel

# --------------------------------- Inicio de cálculo de transiciones --------------------------------#


# ------------ Separar por oraciones ------------------#
with open('Uvieta_original_lematizado.txt') as text:
    mi_corpus = text.read()
    mis_sentencias = mi_corpus.split('.') #Separamos por oraciones por cada punto encontrado
    mis_sentencias = [x.strip() for x in mis_sentencias] 
    mis_sentencias = mis_sentencias[:-1]
    
    for index in range(len(mis_sentencias)):
        if mis_sentencias[index][0] == '¡': #Lidiamos con el "¡Qué caray!"
            mis_sentencias[index] = mis_sentencias[index].split('!')        
            mis_sentencias[index][0] += '!'
            mis_sentencias[index][1] = mis_sentencias[index][1].strip(" ") 

    mis_sentencias_copy = []

    for i in mis_sentencias:
        if type(i) == list:
            for index in i:
                mis_sentencias_copy.append(index)
        else:
            mis_sentencias_copy.append(i)

    mis_sentencias = mis_sentencias_copy #Obtenemos nuestra lista de oraciones (lista con listas de oraciones) 

# -------------------Obtenemos el indice apropiado para asignarle su categoría a cada vocablo ----------------------#

mis_palabras = mi_excel['Vocablo'].tolist() #Guarda todos los vocablos en una lista de python

mis_sentencias_separadas = [sentence.split() for sentence in mis_sentencias]
mis_cat_strings = []
sentences = []

counter = 0

for sentence in mis_sentencias_separadas:
    sent = []
    for word in sentence:
        temp = {word: counter}
        sent.append(temp)
        counter += 1   
        if counter > len(mis_categorias) +1:
            break
    sentences.append(sent)    

for s in sentences:
    cats = []
    for d in s:
        (k, v) = list(d.items())[0]
        word_index = v
        cats.append(mis_categorias[v])

    mis_cat_strings.append(cats) #Obtenemos una lista de oraciones en forma de categoria Ex: 'El perro corre' ->[D, N, V]

# -------------------Incluimos la demarcación de inicio (O) y fin (F) en cada sentencia ----------------------#

# Generar una lista de listas de categorias (oraciones) (incluyendo principio y fin)
mis_trans = []
for sentence in mis_cat_strings:
    inicio = 'O'
    final = 'F'
    sentence.insert(0, inicio)
    sentence.insert(len(sentence), final)
    mis_trans.append(sentence)

# ------------------- Unificar todas las sentencias y su inicio/fin ----------------------#

final_trans = [] #Categorias a usar para el calculo 
for lists in mis_trans:
    for cat in lists:
        final_trans.append(cat)

# ------------ Calcular transiciones ------------------#

mis_trans = dict(Counter(zip(final_trans[:-1],final_trans[1:]))) #Trancisiones 

# ------------ Insertamos inicio y fin a las categorias ------------------#

categorias.insert(0,'O')
categorias.insert(len(categorias),'F') 

trans_xlx = dict.fromkeys(categorias, 0)
trans_list = list(mis_trans.keys())
trans_list_values = list(mis_trans.values())

# ------------ Crea diccionario vacío------------------#

for key in trans_xlx:
        trans_xlx[key] = dict.fromkeys(categorias, 0)


# ------------ Llena diccionario según la data ------------------#
for key in trans_xlx:
    if key == 'F':
        break
    else:
        for trans in trans_list:
            i = trans_list.index(trans)
            if key == trans[0]:
                mi_cat_temp = trans[0]
                trans_temp = trans[1]
                mi_trans_value = trans_list_values[i]                
                trans_xlx[key][trans_temp] = mi_trans_value

# #-------------------Pasamos nuestras transiciones a dataframe y a excel ---------------------------------------#

trans_df = pd.DataFrame(trans_xlx) #Pasamos a dataframe
trans_df_count = trans_df.transpose()

# display(trans_df_count)
send_to_excel_sheet(df=trans_df_count, sheet_name='Trans Count') #Enviamos esto a un sheet en excel

# #-------------------Ocupamos contar nuevamente las categorias, para incluir el inicio y final de cada oración
#Cada oración tiene un inicio y un fin, tenemos tantas ocurrencias (de O y F) como oraciones ---------------------------------------#


ocurrencias_inicio_fin = len(mis_sentencias_separadas) 
cuenta_categorias['O'] = ocurrencias_inicio_fin 
cuenta_categorias['F'] = ocurrencias_inicio_fin

# ------------ Calculamos la probabilidad de transicion, ocurrencia/total de ocurrencia por categoria ------------------#

# print(cuenta_categorias)
for column in trans_df:
    # print (f"Mi columna es {column}")
    mi_columna = column
    for cat in cuenta_categorias:
        # print(f'Mi categoría es {cat}')
        if column == cat:
           trans_df[column] = trans_df[column] / cuenta_categorias[cat]

trans_df = trans_df.transpose()

# send_to_excel_sheet(df=trans_df, sheet_name="Trans probabilities") #Enviamos esto a un sheet en excel también
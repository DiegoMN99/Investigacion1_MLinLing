from csv import writer
import pandas as pd


#Extrae datos del corpus (texto)
with open('Uvieta_original_formatteado.txt') as text:
    mi_corpus = text.read()
    mis_palabras = mi_corpus.split() #Tokenización - separamos el corpus en una lista de palabras individuales

# Crear la hoja de cálculo para la codificación manual

writer = pd.ExcelWriter('Lematización y Codificación Uvieta - Anotador X.xlsx', engine= 'xlsxwriter') # Crear la hoja en sí (vacía)


df = pd.DataFrame({'Vocablo': mis_palabras, 'Lema': '', 'Categoría': ''}) # Crear columnas en el dataframe de pandas, incluyendo nuestras palabras previamente extraidas y separadas


df.to_excel(writer, sheet_name='Sheet1', index=False) # Convierte el dataframe a excel y lo inserta en la hoja de cálculo


writer.save() # Cierra el archivo
print ("Listo! 🥳 El excel se encuentra en la carpeta 🙂")





#Script para normalizar el texto, inspirado en el trabajo de Jorge Antonio Leoni de León -Diego Morales"


import re   # Carga  el paquete de las expresiones regulares
import string


#Formattear el texto, eliminando espacios y elementos innecesarios

def corpus_cleaner(corpus_original):
    with open(corpus_original, "r", encoding="utf8") as file:
        mi_texto = file.readlines()
        file.close
    mi_texto = [x.strip() for x in mi_texto] # Elimina espacio en blanco al final
    mi_texto = [x.lower() for x in mi_texto] # Convierte todas las mayúsculas en minúsculas
    mi_texto = [re.sub('[?¿,—]', '', x, flags = re.M) for x in mi_texto] #elimina puntuación
    mi_texto = [re.sub('  ', '', x, flags = re.M) for x in mi_texto] #elimina espacios dobles
    # mi_texto = [x.translate(str.maketrans('', '', string.punctuation)) for x in mi_texto] #Correr si se desea eliminar puntos finales
    mi_texto = ' '.join(mi_texto)
    texto_formateado = open(file.name[:len(file.name) - 4] + '_lematizado.txt','w+')
    texto_formateado.write(str(mi_texto))
    texto_formateado.close
    print("Archivo formatteado!🥳 Por favor checkear la carpeta")
    return mi_texto

corpus_cleaner(corpus_original='Uvieta_original.txt')
# -*- coding: utf-8 -*-
"""
Acá registro las respuestas de los participantes y actualizo tanto el df con la informacion,
como el modelo usando la funcion exp.update
"""
import pandas as pd

df = pd.DataFrame(columns=['Trial', 'Diseño', 'Resultado','Numeros','Acierto'])


def agregar_datos( diseño, resultado, numeros, aciertos):
    global df
    new_entry = pd.DataFrame({ 'Diseño': [diseño], 'Resultado': [resultado], 'Numeros': [numeros], 'Acierto': [aciertos]})
    df = pd.concat([df, new_entry], ignore_index=True)
    df['Trial'] = range(1, len(df) + 1) 

def process_response(exp, d1, respuesta,numeros):
    aciertos=0
    prom_fijo=50
    d= [41, 44, 46, 48, 49, 51, 52, 54, 56, 59]
    if respuesta == ['left'] and d[d1] < prom_fijo:
        aciertos += 1
    if respuesta == ['right'] and d[d1] > prom_fijo:
        aciertos += 1

    y = 1 if respuesta == ['left'] else 0
    exp.update(d1, y)
    agregar_datos(d[d1], y,numeros,aciertos)
    
    
    

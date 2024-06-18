# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 14:00:05 2024

@author: C_Gab
"""

# main.py
from Exp_v2 import Experiment,exp
from Num_v2 import NumberGenerator
from Resp_v2 import process_response,df

# Variables de configuración
avatar = "X"
edad = 30


# Inicializar la instancia de Experiment una sola vez
# exp = Experiment()

generator = NumberGenerator(exp)

# Generar números y procesar respuesta
numeros, d1 = generator.generate_numbers()
# print("Números generados:", numeros,d[d1],np.mean(numeros))

# Simular una respuesta del participante
respuesta = ['left']  # Ejemplo de respuesta

# Procesar la respuesta
process_response(exp, d1, respuesta,  avatar, edad,numeros)

# Mostrar el dataframe actualizado
print("Datos recopilados:")
print(df)

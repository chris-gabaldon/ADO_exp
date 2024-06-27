# -*- coding: utf-8 -*-
"""

Esta es la rutina donde se generan la lista de numeros que se debera mostrar en la pantalla.
Llamo al script Exp, porque alli esta la funcion ADO_choose() con la que se genera el promedio real 
de la lista (enrealidad genera un indice).


"""
import numpy as np
from Exp_v2 import Experiment


class NumberGenerator:
    def __init__(self, exp_instance):
        self.exp_instance = exp_instance

    def generate_mean_list(self, mu, std, N):
        numeros = np.random.normal(loc=mu, scale=std, size=N)
        numeros = (numeros - np.mean(numeros)) / np.std(numeros, ddof=0)
        numeros = numeros * std + mu
        rounded_numbers = np.around(numeros)
        rounded_mean = np.mean(rounded_numbers[:-1])
        last_number = mu * N - np.sum(rounded_numbers[:-1])
        final_numbers = list(rounded_numbers[:-1]) + [last_number]
        return final_numbers

    def generate_numbers(self):
        d = [41, 44, 46, 48, 49, 51, 52, 54, 56, 59]
        std = 15
        length = 8
        d1 = self.exp_instance.ADOchoose()
        mu = d[d1]
        numeros = self.generate_mean_list(mu, std, length)
        numeros = [int(numeros[i]) for i in range(length)]
        return numeros, d1
    
    def generate_sequential(self,d1):
        d = [41, 44, 46, 48, 49, 51, 52, 54, 56, 59]
        std = 15
        length = 8
        mu = d[d1]
        numeros = self.generate_mean_list(mu, std, length)
        numeros = [int(numeros[i]) for i in range(length)]
        return numeros

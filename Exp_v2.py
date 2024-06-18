# -*- coding: utf-8 -*-

'''
Este es el algoritmo en sí,aca se genera una matriz que luego se va actualizando a medida que se van 
registrando las respuestas. Tambien genero contadores de trials y de bloques (llamo bloque a 
un conjunto de trials).
'''
# Create class Experiment
import math
import random
import numpy as np


class Experiment:

    def __init__(self):
        self.n = 10  # number of design points
        self.k = 100  # number of likelihood points
        
        eps=1e-100
        k = self.k
        n = self.n
        minSize = 1/(k - 1)
        # likelihood values (v_i in the manuscript)
        v = [i*minSize for i in range(math.ceil(1/minSize)+1)]
        v[0] = eps  # to avoid log(0)
        v[-1] = 1 - eps
        
        # this is the array G in the pseudo-code in figure 3
        p = np.zeros((n, k))
        x = np.ones(k)  # this is the vector V in the pseudo-code in figure 3
        tri = np.triu(np.ones((k, k)))  # this is the H matrix in figure 3

        for i in range(n):  # this is the for loop in figure 3
            p[i] = x
            x = x @ tri

        self.factor = p
        self.ffactor = np.flip(p)  # array J in figure 3

        p = self.ffactor * p  # numbers of models passing by each point n,k

        # total models

        self.m = p[n-1].sum()  # total number of models

        # calculate the bins priors at each design and likelihood point if all models are equally probable
        p = p / p.sum(axis=1)[:, None]

        self.p = p  # BINS PRIORS
        self.k = k
        self.n = n
        self.values = np.array(v)  # likelihood points
        # calculate the M matrices and store them din self.mat
        self.mat, self.invmat = self.calcFullFactorMatrices()
        self.initialEntropy = np.sum(
            np.log2(1/self.p) * self.p)  # initial entropy

    def normalize(v):
        sum = v.sum()
        if sum == 0:
            return v

        return v/sum

    def createPredictor(self):  # calculate marginal probabilty for 1
        return self.p @ self.values

    def reset(self):  # reset the bins priors values considering all monotonic curves equally probable
        self.p = self.factor * self.ffactor
        self.p = self.p / self.p.sum(axis=1)[:, None]

        self.mat, self.invmat = self.calcFullFactorMatrices()

    # if you saved the p and M matrices use this function
    def set_prior_mat(self, p, mat, invmat):
        self.p = p.copy()
        self.mat = mat.copy()
        self.invmat = invmat.copy()

    # if you give a p prior matrix, this function finds M matrices compatible with it
    # here we implement what it is mentioned in the section "Setting arbitrary priors"
    def set_prior(self, p):
        k = self.k
        n = self.n

        # this number is arbitrary and it may be changed if convergence is not achieved
        ind_points = 1000
        values_points = np.linspace(0.8, 0.99, ind_points)
        for i in range(ind_points):
            for a in range(n):
                v = [1]*k
                for j in range(k):
                    if self.p[a][j] > p[a][j]:
                        v[j] = values_points[i]
                # print(v)
                self.bayesUpdate(a, v)
        self.initialEntropy = np.sum(np.log2(1/self.p) * self.p)

    # it generates all the Experiment parameters using n desings and k likelihoods
    def generate(self, n, k):
        eps=1e-100
        minSize = 1/(k - 1)
        # likelihood values (v_i in the manuscript)
        v = [i*minSize for i in range(math.ceil(1/minSize)+1)]
        v[0] = eps  # to avoid log(0)
        v[-1] = 1 - eps

        # this is the array G in the pseudo-code in figure 3
        p = np.zeros((n, k))
        x = np.ones(k)  # this is the vector V in the pseudo-code in figure 3
        tri = np.triu(np.ones((k, k)))  # this is the H matrix in figure 3

        for i in range(n):  # this is the for loop in figure 3
            p[i] = x
            x = x @ tri

        self.factor = p
        self.ffactor = np.flip(p)  # array J in figure 3

        p = self.ffactor * p  # numbers of models passing by each point n,k

        # total models

        self.m = p[n-1].sum()

        # calculate the bins priors at each design and likelihood point if all models are equally probable
        p = p / p.sum(axis=1)[:, None]

        self.p = p  # BINS PRIORS
        self.hperpoint = p * self.m
        self.k = k
        self.n = n
        self.values = np.array(v)  # likelihood points
        # calculate the M matrices and store them in self.mat
        self.mat, self.invmat = self.calcFullFactorMatrices()
        self.initialEntropy = (np.log2(self.m/self.hperpoint)
                               * self.p).sum()  # initial entropy

    # updated the bins priors and M matrices based on the likelihoods of the result (v) at the given design point
    # here we implement the algorithm explained in the section "Bayesian update for discrete priors"
    def bayesUpdate(self, design, v):
        eps=1e-100
        aux = self.p[design].copy()
        self.p[design] *= v
        self.p[design] /= self.p[design].sum()
        v = self.p[design]/aux  # used in forwad propagation
        v[aux < eps] = eps
        vv = v  # used in backward propagation

        # update bins priors at desing point to the right of the design point where the measurement was performed
        for i in range(design + 1, self.n):
            aux = self.p[i].copy()
            self.mat[i-1] *= v[np.newaxis, :].T
            self.p[i] = self.mat[i-1].sum(axis=0)
            self.p[i] /= self.p[i].sum()
            v = self.p[i]/aux
            v[aux < eps] = eps

        # update bins priors at desing point to the left of the design point where the measurement was performed
        for i in range(design-1, -1, -1):
            aux = self.p[i].copy()
            self.mat[i] *= vv
            self.p[i] = self.mat[i].sum(axis=1)
            self.p[i] /= self.p[i].sum()
            vv = self.p[i]/aux
            vv[aux < eps] = eps

        self.p[self.p < eps] = eps  # to avoid log(0)
        self.mat[self.mat < eps] = eps  # to avoid log(0)

    # update function. it establishes the likelihood of the result and
    # calls the function to update the bins priors based on these likelihoods
    def update(self, design, result):
        v = self.values
        if result == 1:
            v = 1-v

        self.bayesUpdate(design, v)
    # def update(self, design, result):
    #     v_ = np.zeros_like(self.values)
    #     for i, value in enumerate(self.values):
    #         v_[i] = stats.norm.pdf(result, loc=value, scale=1)

    #     self.bayesUpdate(design, v_)

    # calculate the M matrices

    def calcFullFactorMatrices(self):
        mat = []
        invmat = []

        for i in range(self.n-1):
            m = self.calcFactorMatrix(i, i+1)
            mat.append(m)
            invmat.append(np.linalg.inv(m))

        # return mat,invmat
        return np.array(mat), np.array(invmat)

    def calcFactorMatrix(self, i, j):
        ret = np.zeros((self.k, self.k))

        for a in range(self.k):
            for b in range(self.k):
                ret[a, b] = self.calcFactor(i, a, j, b)

        return ret/ret.sum()

    def calcFactor(self, x0, y0, x1, y1):
        if x1 < x0:
            x1, x0 = x0, x1
            y1, y0 = y0, y1

        if y1 < y0:
            return 0

        dx = x1-x0
        dy = y1-y0

        if dx == 0:
            if dy == 0:
                center = 1
            else:
                center = 0
        else:
            center = (self.factor[dx-1, dy])

        return self.factor[x0, y0] * center * self.ffactor[x1, y1]

    # take a random model from the p and M matrices
    def getRandomModel(self):
        groundtruth = np.zeros(self.n)
        aux = 0
        for i in range(0, self.n - 1):
            aux = random.choices(np.arange(aux, self.k, 1),
                                 weights=self.mat[i].sum(axis=1)[aux:self.k])
            aux = aux[0]
            groundtruth[i] = aux

        aux = random.choices(np.arange(aux, self.k, 1), weights=self.mat[i].sum(
            axis=0)[aux:self.k])  # modificado
        aux = aux[0]
        groundtruth[i + 1] = aux

        return groundtruth

   # calculate the bins prior that would result from
   # a given result witt likelihood v at a given design point
    def bayesCalcExpectedGainAll(self, design, v):
        eps=1e-100
        aux = self.p[design].copy()
        p = self.p.copy()
        mat = self.mat.copy()
        p[design] *= v
        p[design] /= p[design].sum()
        v = p[design]/aux  # used in forwad propagation
        v[aux < eps] = 0
        vv = v  # used in backward propagation

        for i in range(design + 1, self.n):
            aux = self.p[i].copy()
            mat[i-1] *= v[np.newaxis, :].T
            p[i] = mat[i-1].sum(axis=0)
            v = p[i]/aux
            v[aux < eps] = 0

        for i in range(design-1, -1, -1):
            aux = self.p[i].copy()
            mat[i] *= vv
            p[i] = mat[i].sum(axis=1)
            vv = p[i]/aux
            vv[aux < eps] = 0

        p[p < eps] = eps  # to avoid log(0)
        return p

    # # calculate the expected gain at each design point
    def CalcExpectedGainAll(self):
        eps=1e-100
        gain = np.zeros(self.n)
        # to store info gained at each design if the result is 1
        infoG1 = np.zeros(self.n)
        # to store info gained at each design if the resul is 0
        infoG0 = np.zeros(self.n)
        p1 = self.createPredictor()
        p0 = 1-p1
        for i in range(self.n):
            v = self.values.copy()
            info1 = self.bayesCalcExpectedGainAll(i, v)
            v = 1-v
            info0 = self.bayesCalcExpectedGainAll(i, v)

            info1 = np.log2(info1/self.p)*info1
            # info1[self.p<eps] = 0
            info1 = info1.sum()

            info0 = np.log2(info0/self.p)*info0
            # info0[self.p<eps] = 0
            info0 = info0.sum()

            infoG1[i] = info1
            infoG0[i] = info0

            # expected info gain at each design
            gain[i] = p1[i]*info1 + p0[i]*info0

        self.infoG1 = infoG1
        self.infoG0 = infoG0

        return gain

    # chose the design that maximizes the expected gain
    def ADOchoose(self):
        a = np.argmax(self.CalcExpectedGainAll())
        return a

    # chose a random design value
    def RANDchoose(self):
        a = random.randint(0, self.n-1)
        return a

    # calculate the info gained in relation to the prior
    def infoGained(self):
        bits = np.log2(1/self.p) * self.p
        bits[self.p < eps] = 0
        bits = np.sum(bits)
        bits = self.initialEntropy - bits

        return bits

    # calculate the normalized info gain
    def infoProgress(self):
        return self.infoGained() / self.initialEntropy
    
exp=Experiment()
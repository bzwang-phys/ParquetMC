import numpy as np
from utility import *
import numpy.linalg as linalg
from color import *


class grid:
    def __init__(self, para):
        self.Para = para
        self.TauSize = para.TauGridSize
        self.MomSize = para.MomGridSize
        self.AngSize = para.AngGridSize

        #### Grid ############################
        self.TauGrid, self.dTauGrid = self.__TauGrid()
        self.MomGrid = self.__MomGrid()
        self.AngGrid = self.__AngleGrid()

    def __TauGrid(self):
        ########### logirthmic grid #####################
        N = self.Para.TauGridSize/2
        a = self.Para.EF*self.Para.Beta/6.0
        b = a/(N-0.5)
        eps = 1.0e-8/self.Para.Beta

        TauGrid = np.zeros(self.TauSize)

        print a, b
        assert a > 1, "Coeff a must be much larger than 1!"
        assert b > 0, "Coeff b must be larger than 0!"

        for i in range(N):
            TauGrid[i] = 0.5*np.exp(-a)*(np.exp(b*i)-1.0)+eps
            # print i, b*i, a
            TauGrid[2*N-1-i] = 1.0-TauGrid[i]

        TauGrid *= self.Para.Beta

        ########## uniform grid  #########################
        # arr = np.array(range(self.TauSize))
        # TauGrid = arr*self.Para.Beta/(self.TauSize-1)
        # TauGrid[0] += 1.0e-8
        # TauGrid[-1] -= 1.0e-8

        ######### set the Tau bin weight  ###############
        dTauGrid = np.zeros_like(TauGrid)
        dTauGrid += 1.0
        # for i, t in enumerate(TauGrid):
        #     if t > 3.0/self.Para.EF and t < self.Para.Beta-3.0/self.Para.EF:
        #         dTauGrid[i] = 8.0
        # dTauGrid[0] = 8.0
        # dTauGrid[-1] = 8.0
        # dTauGrid /= np.sum(dTauGrid)

        # dTauGrid = np.zeros_like(TauGrid)
        # for i in range(1, self.TauSize-1):
        #     dTauGrid[i] = (TauGrid[i+1]-TauGrid[i-1])/2.0

        # dTauGrid[0] = (TauGrid[1]-TauGrid[0])/2.0+TauGrid[0]
        # dTauGrid[-1] = (TauGrid[-1]-TauGrid[-2])/2.0 + \
        #     (self.Para.Beta-TauGrid[-1])

        return TauGrid, dTauGrid

    def __MomGrid(self):
        ##### Uniform Grid #############################
        # arr = np.array(range(self.MomSize))
        # KGrid = arr*self.Para.MaxExtMom/self.MomSize+1.0e-8

        ##### Fermonic Grid ############################
        KGrid = np.zeros(self.MomSize)
        # the momentum scale corresponds to the temperature 1/Beta
        kT = np.sqrt(1.0/self.Para.Beta)
        N = self.MomSize/2
        a = self.Para.kF/kT/3.0
        assert a > 1, "Coeff a must be much larger than 1!"
        # print a

        b = np.log(1.0+np.exp(a))/N
        for i in range(N):
            KGrid[i] = self.Para.kF*(1.0-np.exp(-a)*(np.exp(-b*(i-N))-1.0))
        KGrid[0] = 0.0

        b = np.log(1.0+np.exp(a)*(self.Para.MaxExtMom/self.Para.kF-1.0))/(N-1)
        for i in range(N, 2*N):
            KGrid[i] = self.Para.kF*(1.0+np.exp(-a)*(np.exp(b*(i-N))-1.0))

        return KGrid

    def __AngleGrid(self):
        arr = np.array(range(self.AngSize))
        AngGrid = arr*2.0/self.AngSize-1.0
        return AngGrid


class spectral:
    def __init__(self, para):
        self.Para = para
        ### Spectral represetation  ##########
        self.TauBasisSize = para.TauBasisSize
        self.RealFreqSize = para.RealFreqGridSize
        self.RealFreqGrid = np.linspace(
            -para.MaxRealFreq, para.MaxRealFreq, para.RealFreqGridSize)

    def TauBasis(self, TauGrid, Type, Num):
        """v[0:Num, :] maps N coefficients to Tau, v.T[:, 0:Num] maps Tau to coefficients"""
        _, s, v = self.TauKernel(TauGrid, Type)
        print yellow("Smallest Singular Value: {0} ".format(s[-1]))
        return v.T[:, :Num]

    def MatFreqBasis(self, MatFreqGrid, Type, Num):
        """v[0:Num, :] maps Tau to N coefficients, v.T[:, 0:Num] maps coefficients to Tau"""
        _, s, v = self.MatFreqKernel(MatFreqGrid, Type)
        print yellow("Smallest Singular Value: {0} ".format(s[-1]))
        return v.T[:, :Num]

    def TauKernel(self, TauGrid, Type):
        kernel = np.zeros([self.RealFreqSize, len(TauGrid)])
        for i, w in enumerate(self.RealFreqGrid):
            kernel[i, :] = self.Kernel(w, TauGrid, self.Para.Beta, Type)
        # multiply the kernel with Delta \omega
        kernel *= 2.0*self.Para.MaxRealFreq/self.RealFreqSize/2.0/np.pi
        u, s, v = linalg.svd(kernel)
        return u, s, v

    def MatFreqKernel(self, MatFreqGrid, Type):
        """v[:, 0:N] gives the first N basis for Matsubara frequency axis"""
        kernel = np.zeros([self.RealFreqSize, len(MatFreqGrid)], dtype=complex)
        for i, w in enumerate(self.RealFreqGrid):
            kernel[i, :] = 1.0/(1j*MatFreqGrid+w)
        kernel *= 2.0*self.Para.MaxRealFreq/self.RealFreqSize/2.0/np.pi
        u, s, v = linalg.svd(kernel)
        return u, s, v

    def Kernel(self, w, t, beta, Type):
        if Type == "Fermi":
            x, y = beta*w/2, 2*t/beta-1
            if x > 100:
                return np.exp(-x*(y+1.))
            elif x < -100:
                return np.exp(x*(1.0-y))
            else:
                return np.exp(-x*y)/(2*np.cosh(x))
        else:
            print "Not implemented!"
            raise ValueError


def Kernel(w, t, beta, Type):
    if Type == "Fermi":
        x, y = beta*w/2, 2*t/beta-1
        if x > 100:
            return np.exp(-x*(y+1.))
        elif x < -100:
            return np.exp(x*(1.0-y))
        else:
            return np.exp(-x*y)/(2*np.cosh(x))
    else:
        print "Not implemented!"
        raise ValueError


def TauKernel(Beta, TauGrid, RealFreqGrid, Type):
    dRealFreq = (RealFreqGrid[-1]-RealFreqGrid[0])/len(RealFreqGrid)
    kernel = np.zeros([len(RealFreqGrid), len(TauGrid)])
    for i, w in enumerate(RealFreqGrid):
        kernel[i, :] = Kernel(w, TauGrid, Beta, Type)
    # multiply the kernel with Delta \omega
    return kernel*dRealFreq/2.0/np.pi


def MatFreqKernel(Beta, MatFreqGrid, RealFreqGrid, Type):
    dRealFreq = (RealFreqGrid[-1]-RealFreqGrid[0])/len(RealFreqGrid)
    kernel = np.zeros([len(RealFreqGrid), len(MatFreqGrid)], dtype=complex)
    for i, w in enumerate(RealFreqGrid):
        kernel[i, :] = 1.0/(1j*MatFreqGrid+w)
    return kernel*dRealFreq/2.0/np.pi


def FitData(Data, Num, v):
    assert Num < v.shape[0], "Number of basis is too large!"
    coef = np.dot(Data, v.T[:, :Num])
    fitted = np.dot(coef, v[:Num, :])
    print "Max of |Sigma-Fitted Sigma|: ", np.amax(abs(Data-fitted))
    return fitted, coef


def Data2Spectral(Data, Num, u, s, v):
    ss = np.zeros((v.shape[0], u.shape[0]))
    assert Num < u.shape[0], "Number of basis is too large!"
    assert Num < v.shape[0], "Number of basis is too large!"
    for i in range(Num):
        ss[i, i] = 1.0/s[i]
    InvKernel = np.dot(np.dot(v.T, ss), u.T)
    return np.dot(Data, InvKernel)


def Spectral2Data(spectral, Num, u, s, v):
    ss = np.zeros((u.shape[0], v.shape[0]))
    assert Num < u.shape[0], "Number of basis is too large!"
    assert Num < v.shape[0], "Number of basis is too large!"
    for i in range(Num):
        ss[i, i] = s[i]
    Kernel = np.dot(np.dot(u, ss), v)
    return np.dot(spectral, Kernel)


if __name__ == "__main__":
    Para = param()
    Grid = grid(Para)
    Spectral = spectral(Para)

    with open("grid.data", "w") as f:
        f.writelines("{0} #TauGrid\n".format(Grid.TauSize))
        for t in Grid.TauGrid:
            f.write("{0} ".format(t))
        f.write("\n\n")

        f.writelines("{0} #dTauGrid\n".format(Grid.TauSize))
        for t in Grid.dTauGrid:
            f.write("{0} ".format(t))
        f.write("\n\n")

        f.writelines("{0} #MomGrid\n".format(Grid.MomSize))
        for k in Grid.MomGrid:
            f.write("{0} ".format(k))
        f.write("\n\n")

        f.writelines("{0} #AngGrid\n".format(Grid.AngSize))
        for a in Grid.AngGrid:
            f.write("{0} ".format(a))
        f.write("\n\n")

        basis = Spectral.TauBasis(Grid.TauGrid, "Fermi", Para.TauBasisSize)
        f.writelines("{0} #FermiTauBasis\n".format(Para.TauBasisSize))
        for t in range(Para.TauGridSize):
            for b in range(Para.TauBasisSize):
                f.write("{0} ".format(basis[t, b]))
        f.write("\n\n")

    pass

import numpy as np


class KSE(object):
    def __init__(self, X, latent_dim, init='random'):
        self.X = X.copy()
        self.N = X.shape[0]
        self.D = X.shape[1]
        self.L = latent_dim

        self.Z = None
        if isinstance(init, str) and init in 'random':
            self.Z = np.random.normal(0, 0.1, (self.N, self.D))
        elif isinstance(init, np.ndarray) and init.shape == (self.N, self.D):
            self.Z = init.copy()
        else:
            raise ValueError("invalid init: {}".format(init))

        self.history = {}

    def fit(self, nb_epoch=100, epsilon=0.5, gamma=1.0, sigma=30.0):

        K = np.dot(self.X, self.X.T)
        X2 = np.diag(K)
        alpha = 1.0 / (sigma ** 2.0)

        self.history['z'] = np.zeros((nb_epoch, self.N, self.L))
        self.history['y'] = np.zeros((nb_epoch, self.N, self.D))

        for epoch in range(nb_epoch):
            Delta = self.Z[:, None, :] - self.Z[None, :, :]
            Dist = np.sum(np.square(Delta), axis=2)
            H = np.exp(-0.5 * gamma * Dist)
            H -= H * np.identity(self.N)
            Hprime = H
            G = np.sum(H, axis=1)[:, None]
            GInv = np.reciprocal(G)
            R = H * GInv
            Rprime = Hprime * GInv

            Y = np.dot(R, self.X)
            Y2 = np.sum(np.square(Y), axis=1)
            Gt = np.sum(H, axis=0)[:, None]
            beta0 = np.sum(G) / (np.dot(Gt.T, X2) - np.dot(Gt.T, Y2))
            beta = (G / (1 + G)) * beta0

            U = R - np.identity(self.N)
            Phi = np.dot(U, K)
            PhiBar = np.sum(R * Phi, axis=1)[:, None]
            E = np.diag(U @ K @ U.T)
            # E = np.sum(np.square(Y - self.X), axis=1)

            A = Rprime * (beta * (Phi - PhiBar))
            A += Rprime * (0.5 * (beta * E - 1.0) / (1.0 + G))

            dZ = np.sum((A + A.T)[:, :, None] * Delta, axis=1)
            dZ -= (alpha / gamma) * self.Z

            self.Z += epsilon * dZ

            self.history['z'][epoch] = self.Z
            self.history['y'][epoch] = Y

        return self.history

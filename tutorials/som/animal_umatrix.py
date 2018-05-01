import numpy as np
from tqdm import tqdm

import sys
sys.path.append('../../')

from libs.models.som.som import SOM
from libs.visualization.som.Umatrix import SOM_Umatrix
from libs.datasets.artificial import animal


if __name__ == '__main__':
    nb_epoch = 50
    resolution = 10
    sigma_max = 2.2
    sigma_min = 0.4
    tau = 50
    latent_dim = 2
    seed = 1

    title="animal map"
    umat_resolution = 100 #U-matrix表示の解像度

    X, labels = animal.load_data()

    np.random.seed(seed)

    som = SOM(X, latent_dim=latent_dim, resolution=resolution, sigma_max=sigma_max, sigma_min=sigma_min, tau=tau)
    som.fit(nb_epoch=nb_epoch)

    som_umatrix = SOM_Umatrix(X=X,
                              Z_allepoch=som.history['z'],
                              sigma_allepoch=som.history['sigma'],
                              labels=labels)
    som_umatrix.draw_umatrix()
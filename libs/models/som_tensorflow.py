from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf
from tqdm import tqdm


class SOM:

    #########################################################################################################################
    #
    #  SOM Algorithm, Batch Implementation powered by Tensorflow
    #
    #  TODO :
    #
    #  - Fix an issue that causes visual oscillation while using 3D learning process
    #	 (if it comes from the class)
    #  - Test for match with base Algorithm : problem with the difference in computation betwwen cdist and pairwise_dist
    #  - Meshgrid implementation on Tensorflow ?
    #  
    #########################################################################################################################

    def __init__(self, dim, number_vectors, epochs=50, n=10, m=10, sigma_min=0.3, sigma_max=2.2, tau=50, init='rand'):
        """
        Initializing the SOM Network through a TensorFlow graph

        :param dim: Dimension of the Input Data
        :param number_vectors: Number of Vectors in the Input Data array
        :param epochs: Number of epochs for iteration. Default is 50
        :param n: Length of the visualisation map. Default is 10
        :param m: Width pf the visuqlisqtion map. Default is 10
        :param signa_min: Minimum value for sigma. Default is 0.3
        :param sigma_max: Maximum value for sigma. Default is 2.2
        :param tau: Learning rate. Default is 50

        """
        print('\nInitializing SOM Tensorflow Graph...\n')

        # Parameters initializing
        self.number_vectors = number_vectors
        self.dimension = dim
        self.n = n
        self.m = m
        self.sigma_min = sigma_min
        self.sigma_max = sigma_max
        self.tau = tau
        self.epochs = epochs

        # History saving for BMU, Weights and sigma value
        self.historyZ = np.zeros((epochs, self.number_vectors, 2))
        self.historyY = np.zeros((epochs, self.n * self.m, self.dimension))
        self.historyS = np.zeros(epochs)
        self.historyB = np.zeros((epochs, self.number_vectors, 1))


        # Setting the graph used by TensorFlow
        self.graph = tf.Graph()

        with self.graph.as_default():
            # Placeholder for the Input_data
            self.input_data = tf.placeholder(shape=[self.number_vectors, self.dimension], dtype=tf.float64)

            self.iter_no = tf.placeholder(dtype=tf.float64)

            # Weights vectors (Y), BMU and Vectors image in 2D (Z and Zeta), initialized at random
            self.Y = tf.Variable(tf.random_normal(shape=[self.n * self.m, self.dimension], dtype=tf.float64))
            zeta = np.dstack(np.meshgrid(np.linspace(-1, 1, self.n), np.linspace(-1, 1, self.m))).reshape(self.n*self.m, 2)
            self.Zeta = tf.constant(zeta, dtype=tf.float64)

            if isinstance(init, str) and init == 'rand':
                self.Z = tf.Variable(tf.random_uniform(shape=[self.number_vectors, 2], dtype=tf.float64) * 2.0 - 1.0)

            elif isinstance(init, np.ndarray) and init.shape == (self.number_vectors, 2):
                self.Z = tf.Variable(initial_value=init, dtype=tf.float64)

            else:
                raise ValueError("invalid init: {}".format(init))

            # Variable to store sigma value
            self.sigma_value = tf.Variable(tf.zeros(shape=(), dtype=tf.float64))

            # Assign value of sigma depending on iteration number
            self.sigma_update = tf.assign(self.sigma_value, self.sigma())

            ################################### COOPERATION AND ADAPTATION STEP ########################################

            # Compute & Update the new weights
            self.train_update = tf.assign(self.Y, self.neighboor_update())

            ########################################## COMPETITIVE STEP ################################################

            # Return a list with the number of each Best Best Matching Unit for each Input Vectors
            self.bmu_nodes = self.winning_nodes()

            # BMU Vectors extractions, each vector is a 2 dimension one (for mapping)
            self.Z_update = tf.assign(self.Z,
                                      tf.reshape(tf.gather(self.Zeta, self.bmu_nodes), shape=[self.number_vectors, 2]))

            # Initializing Session and Variable
            self.session = tf.Session()
            self.session.run(tf.global_variables_initializer())

            print('\nReady !\n')

    def neighboor_update(self):
        """
        Computing the new weights for the Weights Tensor (Y)
        See Batch SOM Algorithm for details

        :returns: A Tensor of shape (Number_of_Reference_Vectors, Dimension)
        """

        # Matrix computing distance between each reference vectors and the Best Matching Unit
        # Shape : Number_of_Reference_Vectors x Number_of_Input_Data_Vectors
        H = tf.reshape(tf.pow(self.pairwise_dist(self.Zeta, self.Z), 2), shape=[self.n * self.m, self.number_vectors])

        # Matrix computing the neighboorhood based on the distance Matrix H for each Reference Vectors
        # Shape : Number_of_Reference_Vectors x Number_of_Input_Data_Vectors
        G = tf.reshape(tf.exp(-H / (2 * tf.pow(self.sigma_update, 2))), shape=[self.n * self.m, self.number_vectors])
        # Computing invert Matrix of Sum
        # Shape : Number_of_Reference_Vectors x 1
        L = tf.expand_dims(tf.reduce_sum(G, axis=1), 1)
        Linv = tf.convert_to_tensor(np.reciprocal(L))

        # Matrix computing the sum between the G Matrix and the invertMatrix
        # Shape : Number_of_Reference_Vectors x Number_of_Input_Vectors
        B = G * Linv

        # Computing the wieghts
        # Shape : Number_of_Reference_Vectors x Number_of_Dimensions
        return B @ self.input_data

    def sigma(self):
        """
        Computing the evolution of sigma based on the iteration number
        Wrapping the function max using py_func to get a tensor

        :returns: The value of sigma for this iteration
        """
        return tf.py_func(max, (
            tf.cast(self.sigma_min, tf.float64), tf.cast(self.sigma_max * (1 - (self.iter_no / self.tau)), tf.float64)),
                          tf.float64)

    def winning_nodes(self):
        """
        Return the list of the Best Matching Units by computing the distance between
        the Weights Tensor and the Input Data Tensor

        :returns: A Tensor of shape (Number_of_Input_vectors, 1) containing the list of
        Best Matching Unit
        """
        return tf.transpose(tf.argmin([self.pairwise_dist(self.Y, self.input_data)], 1))

    def pairwise_dist(self, A, B):
        """
        Computes pairwise distances between each elements of A and each elements of B.
        Args:
          A,    [m,d] matrix
          B,    [n,d] matrix
        Returns:
          D,    [m,n] matrix of pairwise distances

        Credits : https://gist.github.com/mbsariyildiz/34cdc26afb630e8cae079048eef91865
        """
        with tf.variable_scope('pairwise_dist'):
            # squared norms of each row in A and B
            na = tf.reduce_sum(tf.square(A), 1)
            nb = tf.reduce_sum(tf.square(B), 1)

            # na as a row and nb as a co"lumn vectors
            na = tf.reshape(na, [-1, 1])
            nb = tf.reshape(nb, [1, -1])

            # return pairwise euclidead difference matrix
            D = tf.sqrt(tf.maximum(na - 2 * tf.matmul(A, B, False, True) + nb, 0.0))
        return D

    def predict(self, data):
        """
        Launch prediction on data

        :param data: An array of data to predict on
        """
        print('\nPredicting out of {0} epochs\n'.format(self.epochs))
        bar = tqdm(range(self.epochs))

        for i in bar:
            # Computing each iteration for the whole batch (ie : Update the weights each iteration) + Saving history
            self.historyS[i], self.historyY[i], self.historyZ[i], self.historyB[i] = self.session.run(
                [self.sigma_update, self.train_update, self.Z_update, self.bmu_nodes],
                feed_dict={self.input_data: data, self.iter_no: i})

        print('\nClosing Tensorflow Session...\n')

        # Closing tf session
        self.session.close()

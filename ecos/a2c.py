import tensorflow as tf
import tensorflow_probability as tfp
import numpy as np

EPSILON = 1e-16

class Actor(tf.keras.Model):
    def __init__(self, action_dim):
        super().__init__()
        self.action_dim = action_dim
        self.dense1_layer = tf.keras.layers.Dense(128, activation=tf.nn.relu)
        self.dense2_layer = tf.keras.layers.Dense(128, activation=tf.nn.relu)
        self.mean_layer = tf.keras.layers.Dense(self.action_dim, activation='softmax')
        self.stdev_layer = tf.keras.layers.Dense(self.action_dim, activation='softmax')

    def call(self, state):
        a1 = self.dense1_layer(state)
        a2 = self.dense2_layer(a1)
        mu = self.mean_layer(a2)

        log_sigma = self.stdev_layer(a2)
        sigma = tf.exp(log_sigma)

        dist = tfp.distributions.Normal(mu, sigma)
        action_ = dist.sample()

        action = tf.tanh(action_)

        log_pi_ = dist.log_prob(action_)

        log_pi = log_pi_ - tf.reduce_sum(tf.math.log(1 - action**2 + EPSILON), axis=1,
                                         keepdims=True)

        return action, log_pi

    @property
    def trainable_variables(self):
        return self.dense1_layer.trainable_variables + \
            self.dense2_layer.trainable_variables + \
            self.mean_layer.trainable_variables + \
            self.stdev_layer.trainable_variables


class Critic(tf.keras.Model):
    def __init__(self):
        super().__init__()
        self.dense1_layer = tf.keras.layers.Dense(32, activation=tf.nn.relu)
        self.dense2_layer = tf.keras.layers.Dense(32, activation=tf.nn.relu)
        self.output_layer = tf.keras.layers.Dense(1)

    def call(self, state, action):
        state_action = tf.concat([state, action], axis=1)
        a1 = self.dense1_layer(state_action)
        a2 = self.dense2_layer(a1)
        q = self.output_layer(a2)

        return q

    @property
    def trainable_variables(self):
        return self.dense1_layer.trainable_variables + \
            self.dense2_layer.trainable_variables + \
            self.output_layer.trainable_variables

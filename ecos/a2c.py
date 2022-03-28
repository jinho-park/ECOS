import tensorflow as tf
import tensorflow_probability as tfp
import numpy as np

EPSILON = 1e-16


class Actor(tf.keras.Model):
    def __init__(self, action_dim):
        super().__init__()
        self.action_dim = action_dim
        self.dense1_layer = tf.keras.layers.Dense(64, activation="relu")
        self.dense2_layer = tf.keras.layers.Dense(64, activation="relu")
        self.mean_layer = tf.keras.layers.Dense(self.action_dim, activation="softmax")

    def call(self, state):
        a1 = self.dense1_layer(state)
        a2 = self.dense2_layer(a1)
        action = self.mean_layer(a2)

        return action

    @property
    def trainable_variables(self):
        return self.dense1_layer.trainable_variables + \
               self.dense2_layer.trainable_variables + \
               self.mean_layer.trainable_variables


class Critic(tf.keras.Model):
    def __init__(self, act_dim):
        super().__init__()
        self.dense1_layer_v = tf.keras.layers.Dense(64, activation="relu")
        self.dense2_layer_v = tf.keras.layers.Dense(64, activation="relu")
        self.output_layer_v = tf.keras.layers.Dense(1)

        # self.dense1_layer_a = tf.keras.layers.Dense(64, activation="relu",
        #                                             kernel_initializer="random_normal",
        #                                             bias_initializer="zeros")
        # self.dense2_layer_a = tf.keras.layers.Dense(64, activation="relu",
        #                                             kernel_initializer="random_normal",
        #                                             bias_initializer="zeros")
        # self.output_layer_a = tf.keras.layers.Dense(act_dim,
        #                                             kernel_initializer="random_normal",
        #                                             bias_initializer="zeros")

    def call(self, state, action):
        state_action = tf.concat([state, action], axis=1)
        v1 = self.dense1_layer_v(state_action)
        v2 = self.dense2_layer_v(v1)
        value = self.output_layer_v(v2)

        # state_action = tf.concat([state, action], axis=1)
        # a1 = self.dense1_layer_a(state_action)
        # a2 = self.dense2_layer_a(a1)
        # adv = self.output_layer_a(a2)
        #
        # adv_ = tf.math.reduce_max(adv - tf.reduce_mean(adv))
        # q = value + adv_

        return value

    @property
    def trainable_variables(self):
        return self.dense1_layer_v.trainable_variables + \
               self.dense2_layer_v.trainable_variables + \
               self.output_layer_v.trainable_variables

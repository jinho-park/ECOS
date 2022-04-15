import numpy as np
import tensorflow as tf
import os
import math
from ecos import a2c
import ray


@ray.remote
class Agent:
    def __init__(self, action_dim, file_path, epoch_step=0, actor_lr_rate=0.0001,
                 critic_lr_rate=0.001, gamma=0.9,
                 polyak=0.99):
        self.policy = a2c.Actor(action_dim)
        self.q1 = a2c.Critic(action_dim)
        self.q2 = a2c.Critic(action_dim)
        self.target_q1 = a2c.Critic(action_dim)
        self.target_q2 = a2c.Critic(action_dim)

        self.file_path = file_path
        self.epoch_step = epoch_step
        # self.writer = tf.summary.create_file_writer('./results')

        self.alpha = tf.Variable(0.0, dtype=tf.float32)
        self.target_entropy = -tf.constant(action_dim, dtype=tf.float32)
        self.gamma = gamma
        self.polyak = polyak

        self.actor_optimizer = tf.keras.optimizers.Adam(actor_lr_rate)
        self.critic_optimizer = tf.keras.optimizers.Adam(critic_lr_rate)
        self.critic2_optimizer = tf.keras.optimizers.Adam(critic_lr_rate)
        self.alpha_optimizer = tf.keras.optimizers.Adam(actor_lr_rate)

        if len(os.listdir(self.file_path)) > 0:
            self.policy.load_weights(self.file_path)

    def sample_action(self, current_state):
        current_state_ = np.array(current_state, ndmin=2)
        action_prob = self.policy.call(current_state_)

        return action_prob[0]

    def sample_value(self, current_state, action, reward, next_state):
        current_state_ = np.array(current_state, ndmin=2)
        action_ = np.array(action, ndmin=2)
        reward_ = np.array(reward, ndmin=2)
        next_state_ = np.array(next_state, ndmin=2)
        q = self.q1.call(current_state_, action_)
        action_prob = self.policy.call(next_state_)
        q_target = self.target_q1.call(next_state_, action_prob)

        td_error = reward_ + self.gamma * q_target - q

        return td_error, q

    def update_q_network(self, current_states, actions, rewards, next_states, weight=1):
        with tf.GradientTape() as tape1:
            q1 = self.q1.call(current_states, actions)

            pi_a = self.policy.call(next_states)

            q1_target = self.target_q1.call(next_states, pi_a)
            q2_target = self.target_q2.call(next_states, pi_a)

            min_q_target = tf.minimum(q1_target, q2_target)

            y = tf.stop_gradient(rewards + self.gamma * min_q_target)

            critic1_loss = tf.reduce_mean((q1 - y)**2*weight)

        with tf.GradientTape() as tape2:
            q2 = self.q2.call(current_states, actions)

            pi_a = self.policy.call(next_states)

            q1_target = self.target_q1.call(next_states, pi_a)
            q2_target = self.target_q2.call(next_states, pi_a)

            min_q_target = tf.minimum(q1_target, q2_target)

            y = tf.stop_gradient(rewards + self.gamma * min_q_target)

            critic2_loss = tf.reduce_mean((q2 - y)**2 * weight)

        grads1 = tape1.gradient(critic1_loss, self.q1.trainable_variables)
        self.critic_optimizer.apply_gradients(zip(grads1, self.q1.trainable_variables))

        grads2 = tape2.gradient(critic2_loss, self.q2.trainable_variables)
        self.critic2_optimizer.apply_gradients(zip(grads2, self.q2.trainable_variables))

        for grad, var in zip(grads1, self.q1.trainable_variables):
            tf.summary.histogram(f"grad-{var.name}", grad, self.epoch_step)
            tf.summary.histogram(f"var-{var.name}", var, self.epoch_step)
        for grad, var in zip(grads2, self.q2.trainable_variables):
            tf.summary.histogram(f"grad-{var.name}", grad, self.epoch_step)
            tf.summary.histogram(f"var-{var.name}", var, self.epoch_step)

        return critic1_loss, critic2_loss

    def update_policy_network(self, current_states):
        with tf.GradientTape() as tape:
            pi_a = self.policy.call(current_states)

            q1 = self.q1.call(current_states, pi_a)
            q2 = self.q2.call(current_states, pi_a)

            min_q = tf.minimum(q1, q2)

            reduce_mean = tf.reduce_mean(min_q)

            actor_loss = -reduce_mean

        grads = tape.gradient(actor_loss, self.policy.trainable_variables)
        self.actor_optimizer.apply_gradients(zip(grads, self.policy.trainable_variables))

        grads_value = 0

        for grad, var in zip(grads, self.q1.trainable_variables):
            tf.summary.histogram(f"grad-{var.name}", grad, self.epoch_step)
            tf.summary.histogram(f"var-{var.name}", var, self.epoch_step)

        assert math.isnan(actor_loss.numpy()) is False, print("reduce_mean:", reduce_mean,
                                                              "q1:", q1, "q2:", q2,
                                                              "state:", current_states)
        assert math.isnan(grads_value) is False, print("grad is nan", grads[-1])

        return actor_loss, grads_value

    def update_alpha(self, current_states):
        with tf.GradientTape() as tape:
            alpha_loss = tf.reduce_mean(- self.alpha*self.target_entropy)

        variables = [self.alpha]
        grads = tape.gradient(alpha_loss, variables)
        self.alpha_optimizer.apply_gradients(zip(grads, variables))

        for grad, var in zip(grads, self.q1.trainable_variables):
            tf.summary.histogram(f"grad-{var.name}", grad, self.epoch_step)
            tf.summary.histogram(f"var-{var.name}", var, self.epoch_step)

        return alpha_loss

    def train(self, current_states, actions, rewards, next_states, weight=None):
        critic1_loss, critic2_loss = self.update_q_network(current_states, actions, rewards,
                                                           next_states, weight=weight)

        actor_loss, grad_value = self.update_policy_network(current_states)

        alpha_loss = self.update_alpha(current_states)

        return critic1_loss, critic2_loss, actor_loss, grad_value, alpha_loss

    def update_weights(self):
        for theta_target, theta in zip(self.target_q1.trainable_variables, self.q1.trainable_variables):
            theta_target = self.polyak * theta_target + (1 - self.polyak) * theta
        for theta_target, theta in zip(self.target_q2.trainable_variables, self.q2.trainable_variables):
            theta_target = self.polyak * theta_target + (1 - self.polyak) * theta

        self.policy.save_weights(self.file_path, save_format="tf")

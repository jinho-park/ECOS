import os
import numpy as np
import tensorflow as tf
import a2c
from ecos.simulator import Simulator

RANDOM_SEED = 42
RAND_RANGE = 1000000
S_INFO = #
S_LEN = 1
A_DIM = Simulator.get_instance().get_num_of_edge()
ACTOR_LR_RATE = 0.0001
CRITIC_LR_RATE = 0.001
TRAIN_SEQ_LEN = 100
MODEL_SAVE_INTERVAL = 100
GRADIENT_BATCH_SIZE = 16
SUMMARY_DIR = './result'
LOG_FILE = './results/log'
NN_MODEL = None


class Agent:
    def __init__(self):
        np.random.seed(RANDOM_SEED)
        self.epoch = 0
        self.time_stamp = 0

        last_collaboration_target = DEFAULT_ACTION
        collaboration_target = DEFAULT_ACTION

        action_vec = np.zeros(A_DIM)
        action_vec[collaboration_target] = 1

        self.s_batch = [np.zeros((S_INFO, S_LEN))]
        self.a_batch = [action_vec]
        self.r_batch = []
        self.entropy_record = []

        self.actor_gradient_batch = []
        self.critic_gradient_batch = []

        self.log_file = open(LOG_FILE, 'wb')

        self.actor = a2c.ActorNetwork(state_dim=[S_INFO, S_LEN],
                                 action_dim=A_DIM, learning_rate=ACTOR_LR_RATE)

        self.critic = a2c.CriticNetwork(state_dim=[S_INFO, S_LEN],
                                   learning_rate=CRITIC_LR_RATE)

        self.summary_ops, self.summary_vars = a2c.build_summaries()

        self.writer = tf.summary.create_file_writer(SUMMARY_DIR)
        self.saver = tf.train.Checkpoint()
        manager = tf.train.CheckpointManager(self.saver)

        nn_model = NN_MODEL
        if nn_model is not None:
            self.saver.restore(manager.latest_checkpoint)
            print("Model restored.")

    def train(self, _state):
        processing, network, buffering, [computing_resource], action = _state

        self.time_stamp = Simulator.get_instance().get_clock()

        reward = ?

        self.r_batch.append(reward)
        last_action = action

        if len(self.s_batch) == 0:
            state = [np.zeros((S_INFO, S_LEN))]
        else:
            state = np.array(self.s_batch[-1], copy=True)

        state = np.roll(state, -1, axis = 1)

        self.entropy_record.append((a2c.compute_entropy(action[0])))

        self.log_file.write(str(self.time_stamp) + '\t' +
                            str(target) + '\t' +
                            str(processing) + '\t' +
                            str(transmission) + '\t' +
                            str(buffer) + '\t' +
                            str(reward) + '\n')
        self.log_file.flush()

        if len(self.r_batch) >= TRAIN_SEQ_LEN:
            actor_gradient, critic_gradient, td_batch = a2c.compute_gradients(s_batch=np.stack(self.s_batch[1:], axis=0),
                                                                              a_batch=np.vstack(self.a_batch[1:]),
                                                                              r_batch=np.vstack(self.r_batch[1:]),
                                                                              actor=self.actor, critic=self.critic)

            td_loss = np.mean(td_batch)

            self.actor_gradient_batch.append(actor_gradient)
            self.critic_gradient_batch.append(critic_gradient)

            print("====")
            print("Epoch", self.epoch)
            print("TD_loss: ",td_loss, " Avg_reward: ", np.mean(self.r_batch), " Avg_entropy: ", np.mean(self.entropy_record))
            print("====")

            summary_str = self.summary((td_loss, np.mean(self.r_batch), np.mean(self.entropy_record)))

            self.writer.add_summary(summary_str)
            self.writer.flush()

            self.entropy_record = []

            if len(self.actor_gradient_batch) >= len(self.critic_gradient_batch):
                assert len(self.actor_gradient_batch) == len(self.critic_gradient_batch)

                for i in range(len(self.actor_gradient_batch)):
                    self.actor.apply_gradients(self.actor_gradient_batch[i])
                    self.critic.apply_gradients(self.critic_gradient_batch[i])

                self.actor_gradient_batch = []
                self.critic_gradient_batch = []

                self.epoch += 1
                if self.epoch % MODEL_SAVE_INTERVAL == 0:
                    save_path = self.saver.save(SUMMARY_DIR + "/nn_model_ep_" +
                                                str(self.epoch) + ".ckpt")
                    print("Model saved in file %s" % save_path)

            del self.s_batch[:]
            del self.a_batch[:]
            del self.r_batch[:]

        self.s_batch.append(state)

        action_vec = np.zeros(A_DIM)
        action_vec[collaboration_target] = 1
        self.a_batch.append(action_vec)

    def get_action(self, _state):
        # processing, network, buffering, [computing_resource], action = _state

        action_prob = self.actor.predict(np.reshape(_state, (1, S_INFO, S_LEN)))
        action_cumsum = np.cumsum(action_prob)

        return (action_cumsum > np.random.randint(1, RAND_RANGE) / float(RAND_RANGE)).argmax()

    def finish_training(self):
        self.log_file.close()

    @tf.function
    def summary(self, data):
        return data

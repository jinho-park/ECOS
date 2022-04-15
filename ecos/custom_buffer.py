import numpy as np


class Custom_PER:
    def __init__(self, state_space, action_space, max_size=100000, eps=1e-2):
        # transition
        self.current_states = np.empty((0, state_space), dtype=np.float64)
        self.actions = np.empty((0, action_space), dtype=np.float64)
        self.rewards = np.empty((0, 1), dtype=np.float64)
        self.next_states = np.empty((0, state_space), dtype=np.float64)

        self.rank_list = np.empty((0, 1), dtype=np.float64)
        self.freq = np.empty((0, 1), dtype=np.float64)

        # PER parameters
        self.max_rank = eps
        self.min_rank = 9999999999

        self.real_size = 0
        self.size = max_size

    def store(self, current_state, action, reward, next_state, td_error, value):
        # delete minimum rank
        if self.real_size >= self.size:
            data_idx = np.argmin(self.current_states)
            self.current_states = np.delete(self.current_states, data_idx, axis=0)
            self.actions = np.delete(self.actions, data_idx, axis=0)
            self.rewards = np.delete(self.rewards, data_idx, axis=0)
            self.next_states = np.delete(self.next_states, data_idx, axis=0)
            self.rank_list = np.delete(self.rank_list, data_idx, axis=0)
            self.freq = np.delete(self.freq, data_idx, axis=0)

        self.current_states = np.append(self.current_states[-self.size:],
                                        np.array(current_state, ndmin=2), axis=0)
        self.actions = np.append(self.actions[-self.size:],
                                 np.array(action, ndmin=2), axis=0)
        self.rewards = np.append(self.rewards[-self.size:],
                                 np.array(reward, ndmin=2), axis=0)
        self.next_states = np.append(self.next_states[-self.size:],
                                     np.array(next_state, ndmin=2), axis=0)
        rank = np.absolute(td_error * value - td_error - value)

        self.rank_list = np.append(self.rank_list[-self.size:],
                                   np.array(rank, ndmin=1), axis=0)
        temp_data = [[0]]
        self.freq = np.append(self.freq[-self.size:],
                              np.array(temp_data, ndmin=1), axis=0)

        if rank > self.max_rank:
            self.max_rank = rank
        if rank < self.min_rank:
            self.min_rank = rank

        self.real_size = min(self.size, self.real_size + 1)

    def fetch_sample(self, num_samples):
        # assert self.real_size >= num_samples, "buffer contains less samples than batch size"
        if num_samples > self.real_size:
            num_samples = self.real_size

        rank_sum = sum(self.rank_list + self.min_rank)
        priority = (self.rank_list + self.min_rank) / rank_sum
        priority_ = priority.flatten()

        sample_idxs = np.random.choice(len(self.rank_list), num_samples, p=priority_)

        weights = (1 / (priority[sample_idxs] * num_samples))

        self.freq[sample_idxs] = self.freq[sample_idxs] + 1

        current_state_ = self.current_states[sample_idxs]
        actions_ = self.actions[sample_idxs]
        rewards_ = self.rewards[sample_idxs]
        next_states_ = self.next_states[sample_idxs]

        return current_state_, actions_, rewards_, next_states_, weights

    def get_size(self):
        return self.real_size

    def get_sharing_data(self, percentage):
        num_sample = int(percentage * self.real_size)
        data_idx = sorted(range(len(self.rank_list)), key=lambda i: self.rank_list[i])[-num_sample:]

        current_state_ = self.current_states[data_idx]
        actions_ = self.actions[data_idx]
        rewards_ = self.rewards[data_idx]
        next_state_ = self.next_states[data_idx]
        rank_ = self.rank_list[data_idx]

        return current_state_, actions_, rewards_, next_state_, rank_

    def replace(self, current_states, actions, rewards, next_states, rank_, num_sample):
        data_idx = sorted(range(len(self.rank_list)), key=lambda i: self.rank_list[i])[-num_sample:]
        self.current_states = np.delete(self.current_states, data_idx, axis=0)
        self.actions = np.delete(self.actions, data_idx, axis=0)
        self.rewards = np.delete(self.rewards, data_idx, axis=0)
        self.next_states = np.delete(self.next_states, data_idx, axis=0)
        self.rank_list = np.delete(self.rank_list, data_idx, axis=0)
        self.freq = np.delete(self.freq, data_idx, axis=0)

        dummy_data = [[0] for i in range(num_sample)]
        # print("dummy", dummy_data, "current_states:", current_states)

        self.current_states = np.concatenate([self.current_states, current_states], axis=0)
        self.actions = np.concatenate([self.actions, actions], axis=0)
        self.rewards = np.concatenate([self.rewards, rewards], axis=0)
        self.next_states = np.concatenate([self.next_states, next_states], axis=0)
        self.rank_list = np.concatenate([self.rank_list, rank_], axis=0)
        self.freq = np.concatenate([self.freq, dummy_data], axis=0)

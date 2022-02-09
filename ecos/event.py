class Event:
    def __init__(self, msg, task, time):
        self.msg = msg
        self.task = task
        self.time = time

    def get_message(self):
        return self.msg

    def get_task(self):
        return self.task

    def get_time(self):
        return self.time

    def update_time(self, _time):
        self.time = _time

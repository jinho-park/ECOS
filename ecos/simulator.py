from enum import Enum

# 2022.01.07
class Simulator:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = Simulator()
        return cls._instance

    def __init__(self, _terminateTime,
                 _sim_scenario,
                 _orchestrator_policy,
                 _scenario_factory,
                 _num_device):
        self.taskQueue = list()
        self.eventTag = Enum("send",
                             "create",
                             "processing",
                             "transmission",
                             "progress",
                             "stop")
        self.entity_state = Enum("FINISHED", "RUNNABLE")
        self.running = False
        self.clock = 0
        self.terminateTime = _terminateTime
        self.abruptTerminate = False
        self.sim_scenario = _sim_scenario
        self.orchestrator_policy = _orchestrator_policy
        self.scenario_factory = _scenario_factory
        self.num_device = _num_device
        self.entities = [_scenario_factory.edgeserver_manager(),
                         _scenario_factory.cloudserver_manager(),
                         _scenario_factory.mobileserver_manager()]

    def start_simulator(self):
        #
        print("start simulation")

        self.run()

    def run(self):
        if self.running is False:
            self.running = True
            self.clock = 0

        while True:
            if self.run_clock_tick() or self.abruptTerminate:
                break

            if self.clock >= self.terminateTime and self.terminateTime > 0.0:
                self.stop_simulator()
                self.clock = self.terminateTime
                break

        clock = self.clock()

        self.finish_simulation()
        self.run_stop()

        return clock

    def run_stop(self):
        print("Simulation Stop")

    def finish_simulation(self):
        #
        if self.abruptTerminate is True:
            for ent in self.entities:
                if ent.get_state() != self.entity_state.FINISHED:
                    ent.run()

        for ent in self.entities:
            ent.shutdown_entity()

    def run_clock_tick(self):
        #
        entities_size = self.entities.size()
        queue_empty = False

        for item in self.entities:
            if item.get_state() == self.entity_state.RUNNABLE:
                item.run()

        if len(self.taskQueue) > 0:
            event_list = list()
            event = None
            # integer max value
            time = 9223372036854775807

            for i in self.taskQueue:
                i.get_time()

                if i.get_time < time:
                    time = i.get_time
                    event = i

            event_list.append(event)

            for i in self.taskQueue:
                if event == i:
                    continue

                if time == i.get_time():
                    event_list.append(i)

            self.process_event(event_list)
        else:
            queue_empty = True
            self.running = False
            print("Simulation: No more events")

        return queue_empty

    def process_event(self, event):
        msg = event.get_message()

        # event described by json
        # call the event depend on the function
        if msg.get("task"):
            #
            if msg.get("task") == "create":
                #task create
                task = event.get_task()
                self.scenario_factory.mobile_device_manager(task)
            elif msg.get("task") == "send":
                #send the task
                task = event.get_task()
                self.scenario_factory.network_model.enqueue(task)
            elif msg.get("task") == "processing":
                #task processing in node
                # check each node
                self.scenario_factory.edgeserver_manager.check()
        elif msg.get("network"):
            #
            if msg.get("network") == "transmission":
                self.scenario_factory.network_model.check()
        elif msg.get("simulation"):
            if msg.get("simulation") == "progress":
                #
                progress = (self.clock() * 100)/self.terminateTime

                if progress % 10 == 0:
                    print(progress)
                else:
                    print(".")
            elif msg.get("simulation") == "stop":
                #
                print("100")
                self.finish_simulation()

    def send_event(self, event):
        #
        self.taskQueue.append(event)

    def get_clock(self):
        return self.clock
import json
from enum import Enum


# 2022.01.07
class Simulator:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = Simulator()
        return cls._instance

    def __init__(self):
        self.taskQueue = list()
        self.terminate_time = 0

        # type configuration
        self.eventTag = self.my_enum('send', 'create', 'processing', "transmission", "progress", "stop")
        self.node_type = self.my_enum("Mobile", "Edge", "Cloud")
        self.network_type = self.my_enum("WLAN", "MAN", "WAN")
        self.entity_state = Enum("FINISHED", "RUNNABLE")

        # simulation set
        self.running = False
        self.clock = 0
        self.warmUpPeriod = 0
        self.intervalToGetLoadLog = 0
        self.abruptTerminate = False
        self.sim_scenario = None
        self.orchestrator_policy = None
        self.scenario_factory = None
        self.entities = None
        self.file_log_enable = True

        # network setting
        self.network_properties = None

        # number of computing node setting
        self.minNumOfMobileDevice = 0
        self.maxNumOfMobileDevice = 0
        self.mobileDeviceCounterSize = 0
        self.numOfEdge = 0
        self.num_device = 0

        #server id setting
        #self.CloudId = 0
        #self.EdgeId = 1

        # task configuration
        self.task_look_up_table = list()

    #minseon
    #server edge id setting


    def initialize(self, configure, _network, _app, _num_of_edge):
        self.terminate_time = int(configure["simulation_time"])
        self.orchestrator_policy = configure["orchestration_policy"]
        self.minNumOfMobileDevice = int(configure["min_num_of_mobile_device"])
        self.maxNumOfMobileDevice = int(configure["max_num_of_mobile_device"])
        self.mobileDeviceCounterSize = int(configure["mobile_device_counter"])
        self.sim_scenario = configure["simul_scenario"]
        self.numOfEdge = _num_of_edge
        self.network_properties = _network
        self.task_look_up_table = _app

        return True

    def set_simulation_factory(self, _scenario_factory):
        self.scenario_factory = _scenario_factory
        self.entities = [_scenario_factory.get_edge_manager(),
                         _scenario_factory.get_cloud_manager(),
                         _scenario_factory.get_device_manager()]

    def set_mobile_device(self, _num_device):
        self.num_device = _num_device

    def get_warmup_period(self):
        return self.warmUpPeriod

    def get_load_log_interval(self):
        return self.intervalToGetLoadLog

    def get_file_log_enable(self):
        return self.file_log_enable

    def get_network_properties(self):
        return self.network_properties

    def get_min_num_of_mobile_device(self):
        return self.minNumOfMobileDevice

    def get_max_num_of_mobile_device(self):
        return self.maxNumOfMobileDevice

    def get_num_of_mobile_device(self):
        return self.num_device

    def get_num_of_edge(self):
        return self.numOfEdge

    def get_simulation_scenario(self):
        return self.sim_scenario

    def get_clock(self):
        return self.clock

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

            if self.clock >= self.terminate_time and self.terminate_time > 0.0:
                self.run_stop()
                self.clock = self.terminate_time
                break

        clock = self.clock

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
        entities_size = len(self.entities)
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

    def my_enum(*sequential, **named):
        enums = dict(zip(sequential, range(len(sequential))), **named)
        return type('Enum', (), enums)

    def parse_json_file(self, file):
        json_file = json.dumps(file, indent=4)

        return json_file

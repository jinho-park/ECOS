import json
from enum import Enum
from ecos.event import Event
from ecos.task_generator import Task_generator
from ecos.log import Log


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

        #minseon server id setting
        #self.CloudId = None
        #self.EdgeId = None

        # task configuration
        self.task_look_up_table = list()
        self.task_generator = None



    def initialize(self, configure, _network, _app, _num_of_edge):
        self.terminate_time = int(configure["simulation_time"]) * 60
        self.orchestrator_policy = configure["orchestration_policy"]
        self.minNumOfMobileDevice = int(configure["min_num_of_mobile_device"])
        self.maxNumOfMobileDevice = int(configure["max_num_of_mobile_device"])
        self.mobileDeviceCounterSize = int(configure["mobile_device_counter"])
        self.sim_scenario = configure["simul_scenario"]
        self.numOfEdge = _num_of_edge
        self.network_properties = _network
        self.task_look_up_table = _app

        return True

    #minseon
    #def get_cloud_id(self, _scenario_factory):
    #    self.scenario_factory = _scenario_factory
    #    CloudId = _scenario_factory.get_cloud_manager().get

    def set_simulation_factory(self, _scenario_factory):
        self.scenario_factory = _scenario_factory
        self.entities = [_scenario_factory.get_edge_manager(),
                         _scenario_factory.get_cloud_manager(),
                         _scenario_factory.get_device_manager()]

    def set_mobile_device(self, _num_device):
        self.num_device = _num_device
        self.task_generator = Task_generator(_num_device, self.task_look_up_table)

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

            # check entities
            for item in self.entities:
                item.start_entity()

            self.clock = 0

        self.task_generator.create_task(self.terminate_time)

        print("Task creation is completed: ", len(self.task_generator.get_task()))

        # schedule the task
        for task in self.task_generator.get_task():
            event = Event({"task": "create"}, task, task.get_start_time())
            self.send_event(event)

        # schedule main object
        # progress
        event = Event({"simulation": "progress"}, None, self.terminate_time/100)
        self.send_event(event)

        # stop
        event = Event({"simulation": "stop"}, None, self.terminate_time)
        self.send_event(event)

        while True:
            if self.run_clock_tick() and self.abruptTerminate:
                break

            if self.clock >= self.terminate_time > 0.0:
                self.run_stop()
                self.clock = self.terminate_time
                break

        clock = self.clock

        self.finish_simulation()
        self.run_stop()

        return clock

    def run_stop(self):
        for entity in self.entities:
            entity.shutdown_entity()

        self.running = False

    def finish_simulation(self):
        #
        if self.abruptTerminate is True:
            for ent in self.entities:
                if ent.get_state() != self.entity_state.FINISHED:
                    ent.run()

        for ent in self.entities:
            ent.shutdown_entity()

        Log.get_instance().sim_stop()

    def run_clock_tick(self):
        #
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

                if i.get_time() < time:
                    time = i.get_time()
                    event = i

            event_list.append(event)

            for i in self.taskQueue:
                if event == i:
                    continue

                if time == i.get_time():
                    event_list.append(i)

            # remove event in task queue
            for item in event_list:
                self.taskQueue.remove(item)

            for item in self.taskQueue:
                event_time = item.get_time()
                update_time = event_time - event.get_time()

                if update_time < 0:
                    update_time = 0

                item.update_time(update_time)

            # print(event.get_time())
            self.clock += event.get_time()
            self.process_event(event_list)
        else:
            queue_empty = True
            self.running = False
            print("Simulation: No more events")

        return queue_empty

    def process_event(self, event):
        for evt in event:
            msg = evt.get_message()
            # print(msg, ":", evt.get_time())

            # event described by json
            # call the event depend on the function
            if msg.get("task"):
                #
                if msg.get("task") == "create":
                    # task create
                    self.scenario_factory.get_device_manager().get_offload_target(evt.get_task())
                elif msg.get("task") == "send":
                    # send the task
                    task = evt.get_task()
                    self.scenario_factory.network_model.enqueue(task)
                elif msg.get("task") == "processing":
                    # task processing in node
                    # check each node
                    if msg["detail"]["source"] == -1:
                        self.scenario_factory.get_edge_manager().receive_task_from_device(evt)
                    else:
                        self.scenario_factory.get_edge_manager().receive_task_from_edge(evt)
                elif msg.get("task") == "check":
                    if msg["detail"]["node"] == "device":
                        device = self.entities[2].get_node_list()[msg["detail"]["id"]]
                        device.update_task_state(self.clock)
                    elif msg["detail"]["node"] == "edge":
                        edge = self.entities[0].get_node_list()[msg["detail"]["id"]]
                        edge.update_task_state(self.clock)
                    elif msg["detail"]["node"] == "cloud":
                        cloud = self.entities[1].get_node_list()[msg["detail"]["id"]]
                        cloud.update_task_state(self.clock)
            elif msg.get("network"):
                #
                if msg.get("network") == "transmission":
                    self.scenario_factory.network_model.check()
            elif msg.get("simulation"):
                if msg.get("simulation") == "progress":
                    #
                    progress = int((self.clock * 100)/self.terminate_time)

                    if progress % 10 == 0:
                        print(progress, end='')
                    else:
                        print(".", end='')

                    if self.clock <= self.terminate_time:
                        evt.update_time(self.terminate_time/100)
                        self.send_event(evt)

                elif msg.get("simulation") == "stop":
                    #
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

import json
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
        self.loss_result_path = ""
        # all event excluded task creation
        self.taskQueue = list()
        # task create
        self.eventQueue = list()
        self.terminate_time = 0

        # type configuration
        self.eventTag = self.my_enum('send', 'create', 'processing', "transmission", "progress", "stop")
        self.node_type = self.my_enum("Mobile", "Edge", "Cloud")
        self.network_type = self.my_enum("WLAN", "MAN", "WAN")
        self.entity_state = self.my_enum("FINISHED", "RUNNABLE")

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

    def initialize(self, configure, _network, _app, _num_of_edge, policy):
        self.terminate_time = int(configure["simulation_time"]) * 60
        self.warmUpPeriod = int(configure["warmup_time"]) * 60
        self.orchestrator_policy = policy
        self.minNumOfMobileDevice = int(configure["min_num_of_mobile_device"])
        self.maxNumOfMobileDevice = int(configure["max_num_of_mobile_device"])
        self.mobileDeviceCounterSize = int(configure["mobile_device_counter"])
        self.sim_scenario = configure["simul_scenario"]
        self.numOfEdge = _num_of_edge
        self.network_properties = _network
        # self.topology.link_configure(_network)
        self.task_look_up_table = _app

        return True

    def set_loss_folder_path(self, path):
        self.loss_result_path = path

    def get_loss_folder_path(self):
        return self.loss_result_path

    def set_simulation_factory(self, _scenario_factory):
        self.scenario_factory = _scenario_factory
        self.entities = [_scenario_factory.get_edge_manager(),
                         _scenario_factory.get_cloud_manager(),
                         _scenario_factory.get_device_manager()]

    def get_scenario_factory(self):
        return self.scenario_factory

    def set_mobile_device(self, _num_device):
        self.num_device = _num_device
        self.task_generator = Task_generator(_num_device, self.task_look_up_table)

    def get_task_look_up_table(self):
        return self.task_look_up_table

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

    def get_orchestration_policy(self):
        return self.orchestrator_policy

    def get_simulation_scenario(self):
        return self.sim_scenario

    def get_clock(self):
        return self.clock

    def get_warmup_time(self):
        return self.warmUpPeriod

    def start_simulator(self):
        #
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
            event = Event({"task": "create"}, task, task.get_birth_time())
            self.task_event(event)

        self.eventQueue = sorted(self.eventQueue, key=lambda evt: evt.get_time())

        # schedule main object
        # progress
        event = Event({"simulation": "progress"}, None, round(self.terminate_time/100))
        self.send_event(event)

        # stop
        event = Event({"simulation": "stop"}, None, round(self.terminate_time))
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

        # for item in self.entities:
        #     if item.get_state() != self.entity_state.RUNNABLE:
        #         item.run()

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
            time_ = self.eventQueue[0].get_time() - self.clock
            if len(self.eventQueue) > 0 and time_ < event.get_time():
                event = self.eventQueue[0]
                self.eventQueue.remove(event)
                event.update_time(event.get_time() - self.clock)
                event_list.append(event)
                if event.get_time() < 0:
                    print("time error")
                    print("event time: ", event.get_time(), " clock: ", self.clock)
                    exit(1)
            else:
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

                if update_time > 100000:
                    self.taskQueue.remove(item)
                    continue

                if update_time < 0:
                    update_time = 0

                item.update_time(update_time)

            # print(event.get_time())
            self.clock += event.get_time()
            self.process_event(event_list)
        elif len(self.eventQueue) > 0:
            event = self.eventQueue[0]
            self.eventQueue.remove(event)
            event.update_time(self.clock - event.get_time())
            self.clock += event.get_time()
            self.process_event(event)
        else:
            queue_empty = True
            self.running = False
            print("Simulation: No more events")

        return queue_empty

    def process_event(self, event):
        for evt in event:
            msg = evt.get_message()

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
                    elif msg["detail"]["source"] == 0:
                        self.scenario_factory.get_cloud_manager().receive_task(evt)
                    else:
                        self.scenario_factory.get_edge_manager().receive_task_from_edge(evt)
                elif msg.get("task") == "check":
                    if msg["detail"]["node"] == "device":
                        device = self.entities[2].get_node_list()[msg["detail"]["id"]]
                        device.update_task_state(self.clock)
                    elif msg["detail"]["node"] == "edge":
                        edge = self.entities[0].get_node_list()[msg["detail"]["id"] - 1]
                        edge.update_task_state(self.clock)
                    elif msg["detail"]["node"] == "cloud":
                        cloud = self.entities[1].get_node_list()[msg["detail"]["id"]]
                        cloud.update_task_state(self.clock)
                elif msg.get("task") == "offloading":
                    if msg["detail"]["node"] == "edge":
                        edge = self.entities[0]
                        edge.offloading()

                    evt.update_time(0.01)
                    self.send_event(evt)
                    continue
            elif msg.get("network"):
                #
                if msg.get("network") == "transmission":
                    # send task to cloud (finish)
                    if msg["detail"]["type"] == 0:
                        link = msg["detail"]["link"]
                        link.update_send_task(evt.get_task())
                        msgg = {
                            "task": "processing",
                            "detail": {
                                "source": 0
                            }
                        }

                        evt.get_task().set_network_delay(self.get_clock(), 1)
                        evtt = Event(msgg, evt.get_task(), 0)

                        self.send_event(evtt)
                    else:
                        # send task to edge
                        # link
                        link = msg["detail"]["link"]
                        link.update_send_task(evt.get_task())

                        # update msg
                        route_list = msg["detail"]["route"]
                        route_list.remove(int(msg["detail"]["source"]))
                        delay = 0

                        if len(route_list) <= 1:
                            typ = msg["detail"]["type"]
                            msgg = {
                                "task": "processing",
                                "detail" : {
                                    "source": typ,
                                    "route": route_list
                                }
                            }

                            evt.get_task().set_network_delay(self.get_clock(), 2)
                            et = Event(msgg, evt.get_task(), delay)

                            self.send_event(et)
                            continue
                        else:
                            source_edge = route_list[0]
                            dest = route_list[1]

                            # find link
                            for lnk in self.scenario_factory.get_edge_manager().get_link_list():
                                lnk_status = lnk.get_link()
                                set = [source_edge, dest]

                                if sorted(set) == sorted(lnk_status):
                                    updated_link = lnk
                                    delay = lnk.get_download_delay(evt.get_task())

                            msg["detail"]["delay"] = delay
                            msg["detail"]["link"] = updated_link
                            msg["detail"]["source"] = source_edge

                            et = Event(msg, evt.get_task(), delay)

                            self.send_event(et)
                            continue
            elif msg.get("simulation"):
                if msg.get("simulation") == "progress":
                    #
                    progress = int((self.clock * 100)/self.terminate_time)

                    if progress % 10 == 0:
                        print("Progress:", progress, end='')
                    else:
                        print("*", end='')

                    if self.clock < self.terminate_time:
                        evt.update_time(round(self.terminate_time/100))
                        self.send_event(evt)

                elif msg.get("simulation") == "stop":
                    #
                    self.finish_simulation()

    def task_event(self, task_list):
        self.eventQueue.append(task_list)

    def send_event(self, event):
        #
        event.update_time(round(event.get_time(), 6))
        self.taskQueue.append(event)

    def my_enum(*sequential, **named):
        enums = dict(zip(sequential, range(len(sequential))), **named)
        return type('Enum', (), enums)

    def parse_json_file(self, file):
        json_file = json.dumps(file, indent=4)

        return json_file

from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.ai.profiles import DEFAULT_PROFILE, Profile
from rlbot.ai.memory import Memory
from rlbot.ai.model import Model
import rlbot.ai.settings as SETTINGS
import copy, random, math, time

class Context:
    def __init__(self, agent):
        self.agent = agent
        self.raw_memory = Memory(SETTINGS.MAX_STORAGE_SIZE, normalize=False)
        self.select_memory = Memory(SETTINGS.MAX_TRAINING_SIZE, normalize=True)
        self.model = None
        self.profile = DEFAULT_PROFILE
        self.last_saved = None

    def shutdown(self):
        self.model.shutdown()

    def save_state(self):
        pass

    def save(self, forced=False):
        if (forced):
            # save forced (likely shutdown)
            self.save_state()
            self.last_saved = time.time()
        elif (self.last_saved == None or time.time() - self.last_saved >= SETTINGS.TIME_BETWEEN_SAVES):
            # autosave
            self.save_state()
            self.last_saved = time.time()

    def set_profile(self, profile: Profile):
        self.profile = profile
        self.profile.set_index(self.agent.index)
        self.profile.set_team(self.agent.team)
        self.model = Model(self.profile)

    def make_decision(self, packet: GameTickPacket):
        if (self.profile.is_delayed() or self.model == None):
            # execute planned delayed action
            action = self.profile.execute_delay(packet)
            action.set_state(self.agent.controller_state)
            return (None, action)
        # execute model action
        copy_packet = copy.deepcopy(packet)
        action = self.model.make_decision(copy_packet)
        action.set_state(self.agent.controller_state)
        return (copy_packet, action)

    def record_decision(self, decision, result: GameTickPacket):
        if (decision[0] != None):
            # ensure the data can be evaluated correctly
            copy_packet = copy.deepcopy(result)
            assert decision[1] != None
            self.raw_memory.push([decision[0], decision[1], self.profile.get_evaluation(decision[0], copy_packet)])
            if (self.profile.get_finished(decision[0], copy_packet)):
                # finished an attempt, delay before retrying
                self.form_training_set(True)
                self.profile.delay()

    def form_training_set(self, flush: bool):
        # check if memory should be flushed naturally
        if (self.raw_memory.is_full()):
            flush = True
        if (flush):
            # check if trainable data is storable
            trainable_data = self.raw_memory.flush()
            if (trainable_data != None and math.floor(len(trainable_data)*SETTINGS.PERCENTILE_RANGES) > 0):
                # store training data
                assert len(trainable_data) > 0
                trainable_data.sort(key=lambda x: x[2])
                num = math.floor(len(trainable_data)*SETTINGS.PERCENTILE_RANGES)
                for i in range(num):
                    self.select_memory.push(trainable_data[i])
                    self.select_memory.push(trainable_data[-(i+1)])

    def train(self):
        if (self.select_memory.size() >= 2 * SETTINGS.PARTITION_SIZE):
            mem = self.select_memory.get_memory()
            training = mem[:-SETTINGS.PARTITION_SIZE]
            testing = mem[-SETTINGS.PARTITION_SIZE:]
            partitions = math.floor(len(training)/SETTINGS.PARTITION_SIZE)
            for i in range(partitions):
                self.model.train(random.sample(training, SETTINGS.PARTITION_SIZE))
            self.model.test(testing)

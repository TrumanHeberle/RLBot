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
        self.select_memory = Memory(SETTINGS.MAX_TRAINING_SIZE, normalize=True, keep_bounds=True)
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
            evaluation = self.profile.get_evaluation(decision[0], copy_packet)
            self.raw_memory.push([decision[0], decision[1], evaluation])
            self.model.record_evaluation(evaluation)
            if (self.profile.get_finished(decision[0], copy_packet)):
                # finished an attempt, delay before retrying
                self.model.record_achievement(1)
                self.form_training_set(True)
                self.profile.delay()
            else:
                # didn't finish attempt
                self.model.record_achievement(0)

    def form_training_set(self, flush: bool):
        # check if memory should be flushed naturally
        if (self.raw_memory.is_full()):
            flush = True
        if (flush):
            # check if trainable data is storable
            trainable_data = self.raw_memory.flush()
            if (trainable_data != None):
                for data in trainable_data:
                    self.select_memory.push(data)

    def train(self):
        if (self.select_memory.is_full()):
            mem = self.select_memory.flush()
            testing = mem[:SETTINGS.TESTING_SIZE]
            training = mem[SETTINGS.TESTING_SIZE:]
            training.sort(key=lambda x: x[2])
            condensed = [train for train in training if train[2] <= SETTINGS.PERCENTILE_RANGES or train[2] >= 1-SETTINGS.PERCENTILE_RANGES]
            self.model.train(condensed)
            self.model.test(testing)
        else:
            print(self.select_memory.size() / SETTINGS.MAX_TRAINING_SIZE)

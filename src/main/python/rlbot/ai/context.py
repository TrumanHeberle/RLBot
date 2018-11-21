from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.ai.profiles import DEFAULT_PROFILE, Profile
from rlbot.ai.memory import Memory
import rlbot.ai.settings as SETTINGS
import tensorflow, copy, random, math

class Context:
    def __init__(self, agent):
        self.agent = agent
        self.raw_memory = Memory(SETTINGS.MAX_STORAGE_SIZE)
        self.select_memory = Memory(SETTINGS.MAX_TRAINING_SIZE, min=-1, max=1)
        self.profile = DEFAULT_PROFILE

    def set_profile(self, profile: Profile):
        self.profile = profile
        self.profile.set_index(self.agent.index)

    def make_decision(self, packet: GameTickPacket):
        copy_packet = copy.deepcopy(packet)
        action = random.choice(self.profile.actions)
        action.set_state(self.agent.controller_state)
        return (copy_packet, action)

    def record_decision(self, decision, result: GameTickPacket):
        copy_packet = copy.deepcopy(result)
        assert decision[0] != None
        assert decision[1] != None
        self.raw_memory.push([decision[0], decision[1], self.profile.get_evaluation(decision[0], copy_packet)])
        if (self.profile.get_finished(decision[0], copy_packet)):
            # finished an attempt
            return None

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
        if (not self.select_memory.is_empty()):
            print("training")

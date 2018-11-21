from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.ai.profiles import PROFILES
import math, time, random
import rlbot.ai.settings as SETTINGS

class AIBot(BaseAgent):
    def initialize_agent(self):
        #This runs once before the bot starts up
        self.controller_state = SimpleControllerState()
        self.last_time = time.time()
        self.last_valid = False
        self.last_flush = True
        self.last_game_time = -1
        self.decision = None
        self.train_delay = random.randint(0, SETTINGS.TRAINING_FRAME_DELAY)
        self.context.set_profile(PROFILES["KICKOFF"])

    def evaluate_last(self, packet):
        if (self.last_valid):
            assert self.decision != None
            self.context.record_decision(self.decision, packet) # evaluate the last frame
            self.context.form_training_set(False)               # learn and don't flush data
        elif (not self.last_flush):
            self.context.form_training_set(False)               # learn and don't flush data
        else:
            self.context.form_training_set(True)                # learn and flush data

    def evaluate_current(self, packet):
        # check frame actionability
        if (self.last_game_time == -1):
            # invalid frame, first
            self.last_valid = False
            self.last_flush = True
            self.last_time = time.time()
            self.last_game_time = packet.game_info.seconds_elapsed
            return self.controller_state
        if (packet.game_info.seconds_elapsed == self.last_game_time):
            # invalid frame, paused
            self.last_valid = False
            self.last_time = time.time()
            return self.controller_state
        # frame is actionable (could affect the game)
        self.decision = self.context.make_decision(packet)
        if (not packet.game_info.is_round_active):
            # invalid frame, inactive
            self.last_valid = False
            self.last_flush = True
        elif (time.time() - self.last_time > 1/SETTINGS.DECISIONS_PER_SECOND + SETTINGS.ACCEPTABLE_LAG):
            # invalid frame, lag
            self.last_valid = False
            self.last_flush = True
        else:
            # valid frame
            self.last_valid = True
            self.last_flush = False
            self.train_delay -= 1
        # cleanup from an actionable frame
        self.last_time = time.time()
        self.last_game_time = packet.game_info.seconds_elapsed
        return self.controller_state

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.evaluate_last(packet)              # assess the last decision
        assert self.train_delay >= 0
        assert self.train_delay <= SETTINGS.TRAINING_FRAME_DELAY
        if (self.train_delay == 0):             # attempt to train the bot
            self.context.train()
            self.train_delay = SETTINGS.TRAINING_FRAME_DELAY
        return self.evaluate_current(packet)    # determine the current decision

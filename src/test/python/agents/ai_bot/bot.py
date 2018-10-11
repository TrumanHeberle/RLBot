from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
import math, time, random, toml, os

DEFAULT_SETTINGS = {
    "framerate": {
        "spa": 250,
        "lag": 0.25
    }
}

class AIBotInfo:
    def __init__(self):
        # non-user defined variables
        self.last_time = time.time()
        self.time_elapsed = None
        self.last_action = SimpleControllerState()
        self.total_responses = 0
        self.lost_responses = 0
        self.last_active = False
        # get user defined variables
        settings = DEFAULT_SETTINGS
        try:
            settings = {**settings, **toml.load("./src/test/python/agents/ai_bot/settings.toml")}
            settings["framerate"]["spa"] /= 1000
        except Exception as e:
            print("failed to load bot settings: " + str(e))
        # set user defined variables
        self.spa = settings["framerate"]["spa"]
        self.lag = settings["framerate"]["lag"]

class AIBot(BaseAgent):
    def initialize_agent(self):
        """called on bot initialization."""
        self.controller_state = SimpleControllerState()
        self.info = AIBotInfo()
    def change_state(self, packet):
        """called to alter the controller state of the bot."""
        self.context.make_decision(packet)
    def retire(self):
        """called when the bot needs to be shut down."""
        self.context.retire()
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        """called every frame the bot experiences, handles the bot internally."""
        elapsed = time.time() - self.info.last_time
        # ensure match is in progress and in regulated action rates
        if (packet.game_info.seconds_elapsed == self.info.time_elapsed and self.info.last_active):
            # first paused frame
            self.info.last_time = time.time()
            self.info.last_active = False
            self.controller_state = self.info.last_action
        elif (packet.game_info.seconds_elapsed == self.info.time_elapsed):
            # remaining paused frames
            self.info.last_time = time.time()
            self.controller_state = self.info.last_action
        elif (not packet.game_info.is_round_active and self.info.last_active):
            # first inactive frame (kickoff and replays)
            self.info.last_time = time.time()
            self.info.last_active = False
            self.controller_state = self.info.last_action
        elif (not packet.game_info.is_round_active):
            # remaining inactive frames
            self.info.last_time = time.time()
            self.controller_state = self.info.last_action
        elif (elapsed > self.info.spa and elapsed < self.info.spa * (1 + self.info.lag)):
            # acceptable decision lag time
            self.info.last_time = time.time()
            self.info.last_active = True
            self.change_state(packet)
        elif (elapsed > self.info.spa):
            # unacceptable decision lag time
            self.info.last_time = time.time()
            self.info.last_active = True
            self.controller_state = self.info.last_action
            self.lost_responses += 1
        # return bot control decision (controller state)
        self.info.time_elapsed = packet.game_info.seconds_elapsed
        self.info.last_action = self.controller_state
        self.info.total_responses += 1
        return self.controller_state

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
import math, time, random
import actions

APS = 15 # actions per second
SPA = 1/APS

class Atba(BaseAgent):
    def initialize_agent(self):
        #This runs once before the bot starts up
        self.controller_state = SimpleControllerState()
        self.last_time = time.time()

    def change_state(self, packet):
        random.choice(actions.ACTIONS).set_state(self.controller_state)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # regulate action rate
        if (time.time() - self.last_time > SPA):
            self.change_state(packet)
            self.last_time = time.time()

        return self.controller_state

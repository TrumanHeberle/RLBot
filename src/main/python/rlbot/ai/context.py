from rlbot.ai.actions import ACTIONS
import random, tensorflow

class Context:
    def __init__(self, agent):
        self.agent = agent
        # TODO: add tensorflow session, model, and memory

    def make_decision(self, packet):
        random.choice(ACTIONS).set_state(self.agent.controller_state)

from rlbot.ai.actions import ACTIONS
import random, tensorflow as tf, toml, os

DEFAULT_SETTINGS = {
}

class Context:
    def __init__(self, agent):
        self.agent = agent
        self.settings = DEFAULT_SETTINGS
        # get user defined variables
        try:
            self.settings = {**self.settings, **toml.load("./src/main/python/rlbot/ai/settings.toml")}
        except Exception as e:
            print("failed to load ai settings: " + str(e))
        # finish setup
        self.init()
    def init(self):
        """called when the context needs to be initialized."""
        self.session = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))
    def retire(self):
        """called when the context needs to be shut down."""
        if not (self.session):
            raise UserWarning("context may not have been initialized correctly")
            return
        self.session.close()
    def make_decision(self, packet):
        """called when the context is required to make a decision given an input packet."""
        random.choice(ACTIONS).set_state(self.agent.controller_state)

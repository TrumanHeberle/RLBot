class Action:
    def __init__(self, names, keys):
        self.names = names
        self.keys = keys
        self.w = "W" in keys
        self.a = "A" in keys
        self.s = "S" in keys
        self.d = "D" in keys
        self.shift = "SHIFT" in keys
        self.ml = "ML" in keys
        self.mr = "MR" in keys
    def set_state(self, state):
        state.throttle = self.w - self.s
        state.steer = self.d - self.a
        state.pitch = self.s - self.w
        state.yaw = (self.a - self.d) * (not self.shift)
        state.roll = (self.a - self.d) * (self.shift)
        state.jump = self.mr
        state.boost = self.ml
        state.handbrake = self.shift

# list of all actions possible
ACTIONS = [
    Action(["Boost Pitch Down and Yaw Left","Boost Turn Left"],["W","A","ML"]),
    Action(["Boost Pitch Down and Roll Left"],["W","A","SHIFT","ML"]),
    Action(["Pitch Down and Roll Left","Drift Left"],["W","A","SHIFT"]),
    Action(["Turn Left","Pitch Down and Yaw Left"],["W","A"]),
    Action(["Turn Right","Pitch Down and Yaw Right"],["W","D"]),
    Action(["Pitch Down and Roll Right","Drift Right"],["W","D","SHIFT"]),
    Action(["Boost Pitch Down and Yaw Right","Boost Turn Right"],["W","D","ML"]),
    Action(["Boost Pitch Down and Roll Right"],["W","D","SHIFT","ML"]),
    Action(["Boost Pitch Down","Boost Forward"],["W","ML"]),
    Action(["Boost Forward Jump"],["W","ML","MR"]),
    Action(["Forward Jump"],["W","MR"]),
    Action(["Forward","Pitch Down"],["W"]),
    Action(["Yaw Left"],["A"]),
    Action(["Boost Yaw Left"],["A","ML"]),
    Action(["Boost Drift Left","Boost Roll Left"],["A","SHIFT","ML"]),
    Action(["Boost Left Jump"],["A","ML","MR"]),
    Action(["Boost Pitch Up and Yaw Left"],["A","S","ML"]),
    Action(["Boost Pitch Up and Roll Left"],["A","S","SHIFT","ML"]),
    Action(["Left Jump"],["A","MR"]),
    Action(["Backwards Left","Pitch Up and Yaw Left"],["A","S"]),
    Action(["Pitch Up and Roll Left","Reverse Drift Left"],["A","S","SHIFT"]),
    Action(["Roll Left"],["A","SHIFT"]),
    Action(["Backward Right","Pitch Up and Yaw Right"],["S","D"]),
    Action(["Pitch Up and Roll Right","Reverse Drift Right"],["S","D","SHIFT"]),
    Action(["Boost Pitch Up and Yaw Right"],["S","D","ML"]),
    Action(["Boost Pitch Up and Roll Right"],["S","D","SHIFT","ML"]),
    Action(["Boost Pitch Up"],["S","ML"]),
    Action(["Boost Backward Jump"],["S","ML","MR"]),
    Action(["Backward Jump"],["S","MR"]),
    Action(["Backward","Pitch Up"],["S"]),
    Action(["Yaw Right"],["D"]),
    Action(["Roll Right"],["D","SHIFT"]),
    Action(["Right Jump"],["D","MR"]),
    Action(["Boost Yaw Right"],["D","ML"]),
    Action(["Boost Drift Right","Boost Roll Right"],["D","SHIFT","ML"]),
    Action(["Boost Right Jump"],["D","ML","MR"]),
    Action(["Jump"],["MR"]),
    Action(["Boost"],["ML"]),
    Action(["Boost Jump"],["ML","MR"]),
]
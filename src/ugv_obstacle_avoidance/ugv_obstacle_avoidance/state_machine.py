
from enum import Enum, auto


class State(Enum):
    IDLE = auto()
    MOVING = auto()
    AVOIDING = auto()
    TURNING = auto()
    STOPPED = auto()
    RECOVERING = auto()

FRONT_AVOID_DIST = 1.2 
FRONT_STOP_DIST  = 0.5 
FRONT_CLEAR_DIST = 1.2  

class ObstacleAvoidanceFSM:

    def __init__(self, logger_fn=None):
        self._state = State.IDLE
        self.turn_direction = 1
        self._recovering_cycles = 0
        self._recovering_max = 5  
        self._log = logger_fn if logger_fn else print

    @property
    def state(self) -> State:
        return self._state

    def start(self):
        if self._state == State.IDLE:
            self._transition(State.MOVING)

    def update(self, front: float, left: float, right: float, rear: float) -> State:

        s = self._state

        if s == State.IDLE:
            pass

        elif s == State.MOVING:
            if front < FRONT_STOP_DIST:
                self._transition(State.STOPPED)
            elif front < FRONT_AVOID_DIST:
                self.turn_direction = 1 if left >= right else -1
                self._transition(State.AVOIDING)

        elif s == State.AVOIDING:
            self._transition(State.TURNING)

        elif s == State.TURNING:
            if front > FRONT_CLEAR_DIST:
                self._transition(State.MOVING)

        elif s == State.STOPPED:
            self._recovering_cycles = 0
            self._transition(State.RECOVERING)

        elif s == State.RECOVERING:
            self._recovering_cycles += 1
            if self._recovering_cycles >= self._recovering_max:
                self.turn_direction = 1 if left >= right else -1
                self._transition(State.MOVING)

        return self._state

    def _transition(self, new_state: State):
        if new_state != self._state:
            self._log(f'[StateMachine] {self._state.name} -> {new_state.name}')
            self._state = new_state

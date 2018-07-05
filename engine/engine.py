from engine.inconsistency_checker import InconsistencyChecker
from engine.model import Model


class Engine:
    def __init__(self, checker: InconsistencyChecker):
        self.checker = checker
        self.models = []
        # Create initial model which corresponds to the initial state
        self.run()

    # TODO this method will loop through the time points of the initial model
    # We will check observations/action occurrences in the valid scenario and fork models according to
    # https://github.com/vozhyk-/krar-project/issues/3
    def run(self):
        initial_model = Model(self.checker.valid_scenario)
        print('initial_model:\n', initial_model)
        self.models.append(initial_model)

    def fork_model(self, model: Model) -> Model:
        pass

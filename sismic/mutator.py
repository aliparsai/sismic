from sismic import model
from copy import deepcopy


class Mutator(object):
    def __init__(self, statechart: model.Statechart = None):
        self.mutator_type = self.__class__.__name__
        self.statechart = statechart

    def separate_instance(self) -> model.Statechart:
        assert isinstance(self.statechart, model.Statechart)
        return deepcopy(self.statechart)

    def mutate(self) -> list:
        pass


class StateMissing(Mutator):
    def __init__(self, statechart: model.Statechart = None):
        super().__init__(statechart=statechart)
    
    def mutate(self) -> list:
        mutants = list()

        for state_key in self.statechart.states:
            new_mutant = self.separate_instance()
            new_mutant.mutator_type = self.mutator_type

            assert isinstance(new_mutant, model.Statechart)

            # transition_list = new_mutant.transitions_from(state_key)
            # transition_list.extend(new_mutant.transitions_to(state_key))
            #
            # for transition in transition_list:
            #     try:
            #         new_mutant.remove_transition(transition)
            #
            #     except:
            #         continue
                    # print("\nERROR: \n", err)
                    # print("\nLIST: \n", transition_list)

            try:
                new_mutant.remove_state(state_key)

            except:
                # print("\nERROR REMOVING STATE:\n", err, new_mutant.transitions)
                continue

            mutants.append(new_mutant)

        return mutants


class ArcMissing(Mutator):
    def __init__(self, statechart: model.Statechart = None):
        super().__init__(statechart=statechart)
    
    def mutate(self) -> list:
        mutants = list()

        for transition in self.statechart.transitions:
            new_mutant = self.separate_instance()
            assert isinstance(new_mutant, model.Statechart)

            new_mutant.mutator_type = self.mutator_type

            try:
                new_mutant.remove_transition(transition)

            except:
                continue

            mutants.append(new_mutant)

        return mutants


class WrongStartingState(Mutator):
    def __init__(self, statechart: model.Statechart = None):
        super().__init__(statechart=statechart)

    def mutate(self) -> list:
        mutants = list()
        top_level_states = [ state for state in self.statechart.states if self.statechart.parent_for(state) is None ]
        # state_names = set(self.statechart._children.keys())
        # print(top_level_states)

        top_level_states.remove(self.statechart.root)

        for state_name in top_level_states:
            new_mutant = self.separate_instance()
            new_mutant.mutator_type = self.mutator_type
            assert isinstance(new_mutant, model.Statechart)

            new_mutant.root = state_name

            mutants.append(new_mutant)

        for state_key in self.statechart.states:
            state = self.statechart.state_for(state_key)
            if isinstance(state, model.CompositeStateMixin) and hasattr(state, "initial") and state.initial is not None:
                state_names = set(self.statechart.children_for(state_key))
                state_names.remove(state.initial)

                for state_name in state_names:
                    new_mutant = self.separate_instance()
                    new_mutant.mutator_type = self.mutator_type

                    assert isinstance(new_mutant, model.Statechart)

                    new_mutant.state_for(state_key).initial = state_name

                    try:
                        new_mutant.validate()
                    except:
                        continue

                    mutants.append(new_mutant)

        return mutants

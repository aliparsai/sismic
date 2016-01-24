from sismic import model
from sismic import stories
from sismic import interpreter
from sismic import exceptions

from copy import deepcopy


class Mutation(object):
    def __init__(self, statechart: model.Statechart = None):
        self.statechart = statechart
        self.mutants = list()
        self.mutators = None
        self.mutant_status = dict()

    def create_mutants(self):
        # summon all mutators
        self.mutators = Mutator.__subclasses__()

        # mutate the statechart by each mutator
        for mutator in self.mutators:
            mutator_instance = mutator(self.statechart)
            self.mutants.extend(mutator_instance.mutate())

        for mutant in self.mutants:
            self.mutant_status[mutant] = "Survived"

        # return all mutants
        return self.mutants

    @property
    def survived_mutants(self):
        return [mutant for mutant in self.mutants if self.mutant_status[mutant] == "Survived"]

    def evaluate_story(self, story: stories.Story):

        context_original = list()
        configuration_original = list()
        trace_original = list()
        time_original = list()
        steps_original = list()

        original_interpreter = interpreter.Interpreter(self.statechart)
        for item, step_original in story.tell_by_step(original_interpreter):
            steps_original.append(step_original)
            context_original.append(original_interpreter.context)
            configuration_original.append(original_interpreter.configuration)
            trace_original.append(original_interpreter.trace)
            time_original.append(original_interpreter.time)

        # tell_story_original = story.tell(interpreter.Interpreter(self.statechart))
        # assert isinstance(tell_story_original, interpreter.Interpreter)

        kill_count = 0

        for mutant in self.survived_mutants:
            counter = -1
            mutant_interpreter = interpreter.Interpreter(mutant)

            for item, step_mutant in story.tell_by_step(mutant_interpreter):
                counter += 1

                if steps_original[counter] != step_mutant:
                    self.mutant_status[mutant] = "Killed"
                    kill_count += 1
                    break

                if context_original[counter] != mutant_interpreter.context:
                    self.mutant_status[mutant] = "Killed"
                    kill_count += 1
                    break

                if configuration_original[counter] != mutant_interpreter.configuration:
                    self.mutant_status[mutant] = "Killed"
                    kill_count += 1
                    break

                if trace_original[counter] != mutant_interpreter.trace:
                    self.mutant_status[mutant] = "Killed"
                    kill_count += 1
                    break

                if time_original[counter] != mutant_interpreter.time:
                    self.mutant_status[mutant] = "Killed"
                    kill_count += 1
                    break


            # tell_story_mutant = story.tell(interpreter.Interpreter(mutant))
            # assert isinstance(tell_story_mutant, interpreter.Interpreter)

            # except exceptions.NonDeterminismError as err:
            #     print(err)
            #     print(mutant.mutator_type)
            #     print(mutant.states)

            # if tell_story_original.trace != tell_story_mutant.trace or tell_story_original.configuration != tell_story_mutant.configuration or tell_story_original.context != tell_story_mutant.context:
            #     self.mutant_status[mutant] = "Killed"
            #     kill_count += 1

        return kill_count


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
            if state_key == self.statechart.root:
                continue

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
                new_mutant.removed_transition = transition

            except:
                continue

            mutants.append(new_mutant)

        return mutants


class WrongStartingState(Mutator):
    def __init__(self, statechart: model.Statechart = None):
        super().__init__(statechart=statechart)

    def mutate(self) -> list:
        mutants = list()
        top_level_states = [state for state in self.statechart.states if self.statechart.parent_for(state) is None]
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

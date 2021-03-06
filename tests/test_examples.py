import unittest
from sismic import io
from sismic.interpreter import Interpreter
from sismic.model import Event


class ElevatorTests(unittest.TestCase):
    def setUp(self):
        with open('docs/examples/elevator.yaml') as f:
            self.sc = io.import_from_yaml(f)
        self.interpreter = Interpreter(self.sc)
        # Stabilization
        self.interpreter.execute_once()

    def test_init(self):
        self.assertEqual(len(self.interpreter.configuration), 5)

    def test_floor_selection(self):
        self.interpreter.queue(Event('floorSelected', floor=4)).execute_once()
        self.assertEqual(self.interpreter.context['destination'], 4)
        self.interpreter.execute_once()
        self.assertEqual(sorted(self.interpreter.configuration), ['active', 'doorsClosed', 'floorListener', 'floorSelecting', 'movingElevator'])

    def test_doorsOpen(self):
        self.interpreter.queue(Event('floorSelected', floor=4))
        self.interpreter.execute()
        self.assertEqual(self.interpreter.context['current'], 4)
        self.interpreter.time += 10
        self.interpreter.execute()

        self.assertTrue('doorsOpen' in self.interpreter.configuration)
        self.assertEqual(self.interpreter.context['current'], 0)


class ElevatorContractTests(ElevatorTests):
    def setUp(self):
        with open('docs/examples/elevator_contract.yaml') as f:
            self.sc = io.import_from_yaml(f)
        self.interpreter = Interpreter(self.sc)
        # Stabilization
        self.interpreter.execute_once()


class WriterExecutionTests(unittest.TestCase):
    def setUp(self):
        with open('docs/examples/writer_options.yaml') as f:
            self.sc = io.import_from_yaml(f)
        self.interpreter = Interpreter(self.sc)

    def test_output(self):
        scenario = [
             Event('keyPress', key='bonjour '),
             Event('toggle'),
             Event('keyPress', key='a '),
             Event('toggle'),
             Event('toggle_bold'),
             Event('keyPress', key='tous !'),
             Event('leave')
        ]

        for event in scenario:
            self.interpreter.queue(event)

        self.interpreter.execute()

        self.assertTrue(self.interpreter.final)
        self.assertEqual(self.interpreter.context['output'], ['bonjour ', '[b]', '[i]', 'a ', '[/b]', '[/i]', '[b]', 'tous !', '[/b]'])


class RemoteElevatorTests(unittest.TestCase):
    def setUp(self):
        with open('docs/examples/elevator.yaml') as f:
            elevator = io.import_from_yaml(f)
        with open('docs/examples/elevator_buttons.yaml') as f:
            buttons = io.import_from_yaml(f)

        self.elevator = Interpreter(elevator)
        self.buttons = Interpreter(buttons)
        self.buttons.bind(self.elevator)

    def test_button(self):
        self.assertEqual(self.elevator.context['current'], 0)

        self.buttons.queue(Event('button_2_pushed'))
        self.buttons.execute()

        event = self.elevator._external_events.pop()
        self.assertEqual(event.name, 'floorSelected')
        self.assertEqual(event.data['floor'], 2)

        self.buttons.queue(Event('button_2_pushed'))
        self.buttons.execute()
        self.elevator.execute()

        self.assertEqual(self.elevator.context['current'], 2)

    def test_button_0_on_groundfloor(self):
        self.assertEqual(self.elevator.context['current'], 0)

        self.buttons.queue(Event('button_0_pushed'))
        self.buttons.execute()
        self.elevator.execute()

        self.assertEqual(self.elevator.context['current'], 0)

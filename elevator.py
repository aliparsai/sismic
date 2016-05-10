from sismic import model, io, mutation, stories


elevator_yaml = """
statechart:
  name: Elevator
  preamble: |
    current = 0
    destination = 0

    class Doors:
      def __init__(self):
        self.opened = True

      def open(self):
        self.opened = True

      def close(self):
        self.opened = False

    doors = Doors()
  initial state:
    name: active
    parallel states:
      - name: movingElevator
        initial: doorsOpen
        states:
          - name: doorsOpen
            transitions:
              - target: doorsClosed
                guard: destination != current
                action: doors.close()
              - target: doorsClosed
                guard: after(10) and current > 0
                action: |
                  destination = 0
                  doors.close()
          - name: doorsClosed
            transitions:
              - target: movingUp
                guard: destination > current
              - target: movingDown
                guard: destination < current and destination >= 0
          - name: moving
            transitions:
              - target: doorsOpen
                guard: destination == current
                action: doors.open()
            states:
              - name: movingUp
                on entry: current = current + 1
                transitions:
                  - target: movingUp
                    guard: destination > current
              - name: movingDown
                on entry: current = current - 1
                transitions:
                  - target: movingDown
                    guard: destination < current
      - name: floorListener
        initial: floorSelecting
        states:
          - name: floorSelecting
            transitions:
              - target: floorSelecting
                event: floorSelected
                action: destination = event.floor

"""


elevator = io.import_from_yaml(elevator_yaml)
#
# mutants = list()
# mutator1 = mutation.StateMissing(elevator)
# mutants.extend(mutator1.mutate())
# print(len(mutants))
#
# mutator2 = mutation.ArcMissing(elevator)
# mutants.extend(mutator2.mutate())
# print(len(mutants))
#
#
# mutator3 = mutation.WrongStartingState(elevator)
# mutants.extend(mutator3.mutate())
# print(len(mutants))

event_name_list = elevator.events_for()
event_list = [model.Event(event_name, floor=10) for event_name in event_name_list]
# event_list.extend([stories.Pause(10), stories.Pause(5)])
story_list = stories.random_stories_generator_using_mutation(elevator, event_list, 1)

print(story_list)
from sismic import model, io, mutator


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

mutants = list()
# mutator1 = mutator.StateMissing(elevator)
# mutants.extend(mutator1.mutate())

# mutator2 = mutator.ArcMissing(elevator)
# mutants.extend(mutator2.mutate())


mutator3 = mutator.WrongStartingState(elevator)
mutants.extend(mutator3.mutate())



print(mutants)
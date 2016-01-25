from sismic import model, io, mutation, stories


microwave_yaml = """
statechart:
  name: microwave
  description: |
    This microwave expects to receive the following events:
     - unplug: put the statechart in a final configuration
     - startstop: starts or stops the heating
     - toggledoor: opens or closes the door
     - incDuration: add 5 seconds
     - decDuration : substract 5 seconds
    The microwave is bundled with a turntable, a lamp and a door.
  preamble: duration = 0
  initial state:
    name: root
    initial: plugged
    states:
      - name: unplugged
        type: final
      - name: plugged
        transitions:
          - event: unplug
            target: unplugged
        parallel states:
          - name: door
            initial: door.close
            states:
              - name: door.open
                transitions:
                  - target: door.close
                    event: toggledoor
              - name: door.close
                transitions:
                  - target: door.open
                    event: toggledoor
          - name: heating
            initial: heating.off
            states:
              - name: heating.off
                transitions:
                  - target: heating.on
                    event: startstop
                    guard: active('door.close') and duration > 0
                  - event: incDuration
                    action: duration += 5
                  - event: decDuration
                    action: duration = min(duration - 5, 0)
              - name: heating.on
                transitions:
                  - target: heating.off
                    guard: active('door.open')
                  - target: heating.off
                    guard: duration == 0
                  - target: heating.off
                    event: startstop
                  - guard: idle(1)
                    action: duration -= 1
          - name: turntable
            initial: turntable.off
            states:
              - name: turntable.off
                transitions:
                  - guard: active('heating.on')
                    target: turntable.on
              - name: turntable.on
                initial: turntable.turnleft
                transitions:
                  - guard: not active('heating.on')
                    target: turntable.off
                states:
                - name: turntable.turnleft
                  transitions:
                    - guard: after(5)
                      target: turntable.turnright
                - name: turntable.turnright
                  transitions:
                    - guard: after(5)
                      target: turntable.turnleft
          - name: lamp
            initial: lamp.off
            states:
              - name: lamp.off
                transitions:
                  - guard: active('door.open') or active('heating.on')
                    target: lamp.on
              - name: lamp.on
                transitions:
                  - guard: not active('heating.on') and not active('door.open')
                    target: lamp.off

"""


microwave = io.import_from_yaml(microwave_yaml)
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

event_name_list = microwave.events_for()
event_list = [model.Event(event_name) for event_name in event_name_list]
event_list.extend(
        [stories.Pause(1), stories.Pause(15), stories.Pause(10), stories.Pause(5), stories.Pause(4), stories.Pause(3)])
story_list = stories.random_stories_generator_using_mutation(microwave, event_list, 1)

print(story_list)


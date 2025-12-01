import random
from typing import List
from model.Constant import Constant
from model.Reservation import Reservation
from model.Schedule import Schedule
from ga.config import get_config


def encode() -> List[int]:
    config = get_config()
    classes = config.courseClasses
    indiv = []
    for cc in classes:
        day = random.randrange(Constant.DAYS_NUM)
        room = random.randrange(config.numberOfRooms)
        max_start = max(0, Constant.DAY_HOURS - cc.Duration)
        start = random.randrange(max_start + 1)
        indiv.extend([day, room, start])
    return indiv


def decode(indiv: List[int]) -> Schedule:
    config = get_config()
    schedule = Schedule(config)
    classes = config.courseClasses

    for idx, cc in enumerate(classes):
        day = indiv[3*idx]
        room = indiv[3*idx + 1]
        start = indiv[3*idx + 2]

        r = Reservation.getReservation(config.numberOfRooms, day, start, room)
        base = hash(r)

        for h in range(cc.Duration):
            schedule.slots[base + h].append(cc)

        schedule.classes[cc] = base

    schedule.calculateFitness()
    return schedule

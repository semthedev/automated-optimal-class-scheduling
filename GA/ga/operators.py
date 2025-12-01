import random
from typing import Callable, Tuple, List
from model.Constant import Constant


def cx_schedule(ind1: List[int], ind2: List[int]) -> Tuple[List[int], List[int]]:
    size = len(ind1)
    pt1 = random.randrange(0, size, 3)
    pt2 = random.randrange(pt1, size, 3)
    ind1[pt1:pt2], ind2[pt1:pt2] = ind2[pt1:pt2], ind1[pt1:pt2]
    return ind1, ind2


def mut_schedule_factory(config) -> Callable[[List[int], float], Tuple[List[int],]]:
    classes = config.courseClasses

    def mut_schedule(indiv: List[int], indpb: float) -> Tuple[List[int],]:
        size = len(indiv)
        for i in range(0, size, 3):
            if random.random() < indpb:
                indiv[i] = random.randrange(Constant.DAYS_NUM)
            if random.random() < indpb:
                indiv[i+1] = random.randrange(config.numberOfRooms)
            if random.random() < indpb:
                dur = classes[i//3].Duration
                max_start = max(0, Constant.DAY_HOURS - dur)
                indiv[i+2] = random.randrange(max_start + 1)
        return indiv,

    return mut_schedule

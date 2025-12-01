from .Constant import Constant
from .CourseClass import CourseClass
from .Reservation import Reservation
from .Criteria import Criteria
from collections import deque
from random import randrange
from model import Schedule, Criteria, Constant

import numpy as np


class Schedule:
    def __init__(self, configuration):
        self._configuration = configuration
        self._fitness = 0
        slots_length = Constant.DAYS_NUM * Constant.DAY_HOURS * \
            self._configuration.numberOfRooms
        self._slots = [[] for _ in range(slots_length)]

        self._classes = {}

        self._criteria = np.zeros(
            self._configuration.numberOfCourseClasses * len(Criteria.weights), dtype=bool)

        self._diversity = 0.0
        self._rank = 0

        self._convertedObjectives = []
        self._objectives = []

    def copy(self, c, setup_only):
        if not setup_only:
            self._configuration = c.configuration
            self._slots, self._classes = [row[:] for row in c.slots], {
                key: value for key, value in c.classes.items()}
            self._criteria = c.criteria[:]
            self._objectives = c.objectives[:]
            self._fitness = c.fitness

            if c.convertedObjectives is not None:
                self._convertedObjectives = c.convertedObjectives[:]
            return self

        return Schedule(c.configuration)

    def makeNewFromPrototype(self, positions=None):
        new_chromosome = self.copy(self, True)
        new_chromosome_slots, new_chromosome_classes = new_chromosome._slots, new_chromosome._classes

        classes = self._configuration.courseClasses
        nr = self._configuration.numberOfRooms
        DAYS_NUM, DAY_HOURS = Constant.DAYS_NUM, Constant.DAY_HOURS
        for c in classes:
            dur = c.Duration
            day = randrange(DAYS_NUM)
            room = randrange(nr)
            time = randrange(DAY_HOURS - dur)
            reservation = Reservation.getReservation(nr, day, time, room)

            if positions is not None:
                positions.append(day)
                positions.append(room)
                positions.append(time)
            reservation_index = hash(reservation)

            for i in range(dur - 1, -1, -1):
                new_chromosome_slots[reservation_index + i].append(c)

            new_chromosome_classes[c] = reservation_index

        new_chromosome.calculateFitness()
        return new_chromosome

    def makeEmptyFromPrototype(self, bounds=None):
        new_chromosome = self.copy(self, True)
        new_chromosome_slots, new_chromosome_classes = new_chromosome._slots, new_chromosome._classes

        classes = self._configuration.courseClasses
        nr = self._configuration.numberOfRooms
        DAYS_NUM, DAY_HOURS = Constant.DAYS_NUM, Constant.DAY_HOURS
        for c in classes:
            dur = c.Duration

            if bounds is not None:
                bounds.append(DAYS_NUM - 1)
                bounds.append(nr - 1)
                bounds.append(DAY_HOURS - 1 - dur)

            new_chromosome_classes[c] = -1

        return new_chromosome

    def crossover(self, parent, numberOfCrossoverPoints, crossoverProbability):
        if randrange(100) > crossoverProbability:
            return self.copy(self, False)

        n = self.copy(self, True)
        n_classes, n_slots = n._classes, n._slots

        classes = self._classes
        course_classes = tuple(classes.keys())
        parent_classes = parent.classes
        parent_course_classes = tuple(parent.classes.keys())

        size = len(classes)
        cp = size * [False]

        for i in range(numberOfCrossoverPoints, 0, -1):
            check_point = False
            while not check_point:
                p = randrange(size)
                if not cp[p]:
                    cp[p] = check_point = True

        first = randrange(2) == 0

        for i in range(size):
            if first:
                course_class = course_classes[i]
                dur = course_class.Duration
                reservation_index = classes[course_class]
                n_classes[course_class] = reservation_index
                for j in range(dur - 1, -1, -1):
                    n_slots[reservation_index + j].append(course_class)
            else:
                course_class = parent_course_classes[i]
                dur = course_class.Duration
                reservation_index = parent_classes[course_class]
                n_classes[course_class] = reservation_index
                for j in range(dur - 1, -1, -1):
                    n_slots[reservation_index + j].append(course_class)
            if cp[i]:
                first = not first

        n.calculateFitness()
        return n

    def crossovers(self, parent, r1, r2, r3, etaCross, crossoverProbability):
        size = len(self._classes)
        jrand = randrange(size)

        nr = self._configuration.numberOfRooms
        DAY_HOURS, DAYS_NUM = Constant.DAY_HOURS, Constant.DAYS_NUM

        new_chromosome = self.copy(self, True)
        new_chromosome_slots, new_chromosome_classes = new_chromosome._slots, new_chromosome._classes
        classes = self._classes
        course_classes = tuple(classes.keys())
        parent_classes = parent.classes
        parent_course_classes = tuple(parent.classes.keys())
        for i in range(size):
            if randrange(100) > crossoverProbability or i == jrand:
                course_class = course_classes[i]
                reservation1, reservation2 = Reservation.parse(
                    r1.classes[course_class]), Reservation.parse(r2.classes[course_class])
                reservation3 = Reservation.parse(r3.classes[course_class])

                dur = course_class.Duration
                day = int(reservation3.Day + etaCross *
                          (reservation1.Day - reservation2.Day))
                if day < 0:
                    day = 0
                elif day >= DAYS_NUM:
                    day = DAYS_NUM - 1

                room = int(reservation3.Room + etaCross *
                           (reservation1.Room - reservation2.Room))
                if room < 0:
                    room = 0
                elif room >= nr:
                    room = nr - 1

                time = int(reservation3.Time + etaCross *
                           (reservation1.Time - reservation2.Time))
                if time < 0:
                    time = 0
                elif time >= (DAY_HOURS - dur):
                    time = DAY_HOURS - 1 - dur

                reservation = Reservation.getReservation(nr, day, time, room)
                reservation_index = hash(reservation)

                for j in range(dur - 1, -1, -1):
                    new_chromosome_slots[reservation_index +
                                         j].append(course_class)

                new_chromosome_classes[course_class] = reservation_index
            else:
                course_class = parent_course_classes[i]
                dur = course_class.Duration
                reservation = parent_classes[course_class]
                reservation_index = hash(reservation)

                for j in range(dur - 1, -1, -1):
                    new_chromosome_slots[reservation_index +
                                         j].append(course_class)

                new_chromosome_classes[course_class] = reservation_index

        new_chromosome.calculateFitness()

        return new_chromosome

    def repair(self, cc1: CourseClass, reservation1_index: int, reservation2: Reservation):
        nr = self._configuration.numberOfRooms
        DAY_HOURS, DAYS_NUM = Constant.DAY_HOURS, Constant.DAYS_NUM
        slots = self._slots
        dur = cc1.Duration

        if reservation1_index > -1:
            for j in range(dur):
                cl = slots[reservation1_index + j]
                while cc1 in cl:
                    cl.remove(cc1)

        if reservation2 is None:
            day = randrange(DAYS_NUM)
            room = randrange(nr)
            time = randrange(DAY_HOURS - dur)
            reservation2 = Reservation.getReservation(nr, day, time, room)

        reservation2_index = hash(reservation2)
        for j in range(dur):
            slots[reservation2_index + j].append(cc1)

        self._classes[cc1] = reservation2_index

    def mutation(self, mutationSize, mutationProbability):
        if randrange(100) > mutationProbability:
            return

        classes = self._classes
        numberOfClasses = len(classes)
        course_classes = tuple(classes.keys())
        configuration = self._configuration
        nr = configuration.numberOfRooms

        for i in range(mutationSize, 0, -1):
            mpos = randrange(numberOfClasses)
            cc1 = course_classes[mpos]
            reservation1_index = classes[cc1]
            self.repair(cc1, reservation1_index, None)

        self.calculateFitness()

    def calculateFitness(self):
        self._objectives = np.zeros(len(Criteria.weights))
        score = 0
        criteria, configuration = self._criteria, self._configuration
        items, slots = self._classes.items(), self._slots
        numberOfRooms = configuration.numberOfRooms
        DAY_HOURS, DAYS_NUM = Constant.DAY_HOURS, Constant.DAYS_NUM
        daySize = DAY_HOURS * numberOfRooms

        ci = 0
        getRoomById = configuration.getRoomById

        for cc, reservation_index in items:
            reservation = Reservation.parse(reservation_index)
            day, time, room = reservation.Day, reservation.Time, reservation.Room
            dur = cc.Duration
            ro = Criteria.isRoomOverlapped(slots, reservation, dur)
            criteria[ci + 0] = not ro
            r = getRoomById(room)

            criteria[ci + 1] = Criteria.isSeatEnough(r, cc)

            criteria[ci + 2] = Criteria.isComputerEnough(r, cc)

            timeId = day * daySize + time
            po, go = Criteria.isOverlappedProfStudentGrp(
                slots, cc, numberOfRooms, timeId)

            criteria[ci + 3] = not po

            criteria[ci + 4] = not go
            for i in range(len(self._objectives)):
                if criteria[ci + i]:
                    score += 1
                else:
                    score += Criteria.weights[i]
                    self._objectives[i] += 1 if Criteria.weights[i] > 0 else 2
            ci += len(Criteria.weights)

        self._fitness = score / len(criteria)

    def getDifference(self, other):
        return (self._criteria ^ other.criteria).sum()

    def extractPositions(self, positions):
        i = 0
        items = self._classes.items()
        for cc, reservation_index in items:
            reservation = Reservation.parse(reservation_index)

            positions[i] = reservation.Day
            i += 1
            positions[i] = reservation.Room
            i += 1
            positions[i] = reservation.Time
            i += 1

    def updatePositions(self, positions):
        DAYS_NUM, DAY_HOURS = Constant.DAYS_NUM, Constant.DAY_HOURS
        nr = self._configuration.numberOfRooms
        i = 0
        items = self._classes.items()
        for cc, reservation1_index in items:
            dur = cc.Duration
            day = abs(int(positions[i]) % DAYS_NUM)
            room = abs(int(positions[i + 1]) % nr)
            time = abs(int(positions[i + 2]) % (DAY_HOURS - dur))

            reservation2 = Reservation.getReservation(nr, day, time, room)
            self.repair(cc, reservation1_index, reservation2)

            positions[i] = reservation2.Day
            i += 1
            positions[i] = reservation2.Room
            i += 1
            positions[i] = reservation2.Time
            i += 1

        self.calculateFitness()

    @property
    def fitness(self):
        return self._fitness

    @property
    def configuration(self):
        return self._configuration

    @property
    def classes(self):
        return self._classes

    @property
    def criteria(self):
        return self._criteria

    @property
    def slots(self):
        return self._slots

    @property
    def diversity(self):
        return self._diversity

    @diversity.setter
    def diversity(self, new_diversity):
        self._diversity = new_diversity

    @property
    def rank(self):
        return self._rank

    @rank.setter
    def rank(self, new_rank):
        self._rank = new_rank

    @property
    def convertedObjectives(self):
        return self._convertedObjectives

    @property
    def objectives(self):
        return self._objectives

    def resizeConvertedObjectives(self, numObj):
        self._convertedObjectives = np.zeros(numObj)

    def clone(self):
        return self.copy(self, False)

    def dominates(self, other):
        better = False
        for f, obj in enumerate(self.objectives):
            if obj > other.objectives[f]:
                return False

            if obj < other.objectives[f]:
                better = True

        return better

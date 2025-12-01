from .Constant import Constant


class Criteria:
    weights = [0, 0.5, 0.5, 0, 0]

    @staticmethod
    def isRoomOverlapped(slots, reservation, dur):
        reservation_index = hash(reservation)
        cls = slots[reservation_index: reservation_index + dur]
        return any(True for slot in cls if len(slot) > 1)

    @staticmethod
    def isSeatEnough(r, cc):
        return r.NumberOfSeats >= cc.NumberOfSeats

    @staticmethod
    def isComputerEnough(r, cc):
        return (not cc.LabRequired) or (cc.LabRequired and r.Lab)

    @staticmethod
    def isOverlappedProfStudentGrp(slots, cc, numberOfRooms, timeId):
        po = go = False

        dur = cc.Duration
        for i in range(numberOfRooms, 0, -1):
            for j in range(timeId, timeId + dur):
                cl = slots[j]
                for cc1 in cl:
                    if cc != cc1:
                        if not po and cc.professorOverlaps(cc1):
                            po = True
                        if not go and cc.groupsOverlap(cc1):
                            go = True
                        if po and go:
                            return po, go

            timeId += Constant.DAY_HOURS
        return po, go

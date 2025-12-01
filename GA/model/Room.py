class Room:
    _next_room_id = 0

    def __init__(self, name, lab, number_of_seats):
        self.Id = Room._next_room_id
        Room._next_room_id += 1
        self.Name = name
        self.Lab = lab
        self.NumberOfSeats = number_of_seats

    def __hash__(self):
        return hash(self.Id)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not (self == other)

    @staticmethod
    def restartIDs() -> None:
        Room._next_room_id = 0

class Professor:
    def __init__(self, id, name):
        self.Id = id
        self.Name = name
        self.CourseClasses = []

    def addCourseClass(self, courseClass):
        self.CourseClasses.append(courseClass)

    def __hash__(self):
        return hash(self.Id)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not (self == other)

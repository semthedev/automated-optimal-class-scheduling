import codecs
import json
from typing import List
from model.Professor import Professor
from model.StudentsGroup import StudentsGroup
from model.Course import Course
from model.Room import Room
from model.CourseClass import CourseClass


class Configuration:

    def __init__(self):
        self._isEmpty = True
        self._professors = {}
        self._studentGroups = {}
        self._courses = {}
        self._rooms = {}
        self._courseClasses = []

    def getProfessorById(self, id) -> Professor:
        if id in self._professors:
            return self._professors[id]
        return None

    @property
    def numberOfProfessors(self) -> int:
        return len(self._professors)

    def getStudentsGroupById(self, id) -> StudentsGroup:
        if id in self._studentGroups:
            return self._studentGroups[id]
        return None

    @property
    def numberOfStudentGroups(self) -> int:
        return len(self._studentGroups)

    def getCourseById(self, id) -> Course:
        if id in self._courses:
            return self._courses[id]
        return None

    @property
    def numberOfCourses(self) -> int:
        return len(self._courses)

    def getRoomById(self, id) -> Room:
        if id in self._rooms:
            return self._rooms[id]
        return None

    @property
    def numberOfRooms(self) -> int:
        return len(self._rooms)

    @property
    def courseClasses(self) -> List[CourseClass]:
        return self._courseClasses

    @property
    def numberOfCourseClasses(self) -> int:
        return len(self._courseClasses)

    @property
    def isEmpty(self) -> bool:
        return self._isEmpty

    @staticmethod
    def __parseProfessor(dictConfig):
        id = 0
        name = ''

        for key in dictConfig:
            if key == 'id':
                id = dictConfig[key]
            elif key == 'name':
                name = dictConfig[key]

        if id == 0 or name == '':
            return None
        return Professor(id, name)

    @staticmethod
    def __parseStudentsGroup(dictConfig):
        id = 0
        name = ''
        size = 0

        for key in dictConfig:
            if key == 'id':
                id = dictConfig[key]
            elif key == 'name':
                name = dictConfig[key]
            elif key == 'size':
                size = dictConfig[key]

        if id == 0:
            return None
        return StudentsGroup(id, name, size)

    @staticmethod
    def __parseCourse(dictConfig):
        id = 0
        name = ''

        for key in dictConfig:
            if key == 'id':
                id = dictConfig[key]
            elif key == 'name':
                name = dictConfig[key]

        if id == 0:
            return None
        return Course(id, name)

    @staticmethod
    def __parseRoom(dictConfig):
        lab = False
        name = ''
        size = 0

        for key in dictConfig:
            if key == 'lab':
                lab = dictConfig[key]
            elif key == 'name':
                name = dictConfig[key]
            elif key == 'size':
                size = dictConfig[key]

        if size == 0 or name == '':
            return None
        return Room(name, lab, size)

    def __parseCourseClass(self, dictConfig):
        pid = 0
        cid = 0
        dur = 1
        lab = False
        group_list = []

        for key in dictConfig:
            if key == 'professor':
                pid = dictConfig[key]
            elif key == 'course':
                cid = dictConfig[key]
            elif key == 'lab':
                lab = dictConfig[key]
            elif key == 'duration':
                dur = dictConfig[key]
            elif key == 'group' or key == 'groups':
                groups = dictConfig[key]
                if isinstance(groups, list):
                    for grp in groups:
                        g = self.getStudentsGroupById(grp)
                        if g:
                            group_list.append(g)
                else:
                    g = self.getStudentsGroupById(groups)
                    if g:
                        group_list.append(g)

        p = self.getProfessorById(pid)
        c = self.getCourseById(cid)

        if not c or not p:
            return None

        return CourseClass(p, c, lab, dur, group_list)

    def parseFile(self, fileName):
        self._professors = {}
        self._studentGroups = {}
        self._courses = {}
        self._rooms = {}
        self._courseClasses = []

        Room.restartIDs()
        CourseClass.restartIDs()

        with codecs.open(fileName, "r", "utf-8") as f:
            data = json.load(f)

        max_items = 100

        profs = [d for d in data if 'prof' in d][:max_items]
        courses = [d for d in data if 'course' in d][:max_items]

        rooms = [d for d in data if 'room' in d]
        groups = [d for d in data if 'group' in d]
        classes = [d for d in data if 'class' in d]

        data = profs + courses + rooms + groups + classes

        for dictConfig in data:
            for key in dictConfig:
                if key == 'prof':
                    prof = self.__parseProfessor(dictConfig[key])
                    self._professors[prof.Id] = prof
                elif key == 'course':
                    course = self.__parseCourse(dictConfig[key])
                    self._courses[course.Id] = course
                elif key == 'room':
                    room = self.__parseRoom(dictConfig[key])
                    self._rooms[room.Id] = room
                elif key == 'group':
                    group = self.__parseStudentsGroup(dictConfig[key])
                    self._studentGroups[group.Id] = group
                elif key == 'class':
                    courseClass = self.__parseCourseClass(dictConfig[key])
                    if courseClass is not None:
                        self._courseClasses.append(courseClass)

        self._isEmpty = False

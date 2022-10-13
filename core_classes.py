import APIHandler

class Course:
    def __init__(self, courseInfo):
        self.id = courseInfo[0]['course_id']
        self.credits = int(courseInfo[0]['credits'])
        self.prereqs = []
        if courseInfo[0]['relationships']['prereqs'] != None:
            fullPrereqsString = courseInfo[0]['relationships']['prereqs']
            IDindices = []
            for i in range(len(fullPrereqsString)):
                if fullPrereqsString[i].isdigit() and fullPrereqsString[i - 1].isalpha():
                    IDindices.append(i)
            for IDindex in IDindices:
                self.prereqs.append(fullPrereqsString[IDindex - 4 : IDindex + 3])

    def __eq__(self, __o: object) -> bool:
        if type(__o) is Course:
            return self.id ==  __o.id
        elif type(__o) is str:
            return self.id == __o
        else:
            return False

    def __repr__(self) -> str:
        return self.id

class Student:
    def __init__(self, name, coursesTaken):
        self.name = name
        self.coursesTaken = coursesTaken
        self.coursesScheduled = []

    def canTake(self, course):
        numPrereqs = len(course.prereqs)
        for prereq in course.prereqs:
            if prereq in self.coursesTaken or prereq in self.coursesScheduled:
                numPrereqs -= 1
        return numPrereqs == 0 and not course in self.coursesTaken and not course in self.coursesScheduled
    
    def buildCoreSchedule(self, courseList):
        self.schedule = [[], [], [], [], [], [], [], [], []]
        for semester in self.schedule:
            semesterCredits = 0
            for course in courseList:
                if semesterCredits + course.credits <= 12 and self.canTake(course):
                    semester.append(course.id)
                    semesterCredits += course.credits
            for course in semester:
                self.coursesScheduled.append(course)
        
        return self.schedule

def main():
    API = APIHandler.ApiHandler("https://api.umd.io/v1")
    
    student1 = Student("?", ['MATH115', 'MATH131'])
    student2 = Student("??", ['MATH115', 'MATH131', 'MATH140', 'CMSC131'])
    student3 = Student("??", ['MATH115', 'MATH131', 'MATH140', 'CMSC131', 'MATH141'])
    MATH140 = Course(API.getCourseByID("MATH140"))
    CMSC131 = Course(API.getCourseByID("CMSC131"))
    MATH141 = Course(API.getCourseByID("MATH141"))
    CMSC132 = Course(API.getCourseByID("CMSC132"))
    CMSC216 = Course(API.getCourseByID("CMSC216"))
    CMSC250 = Course(API.getCourseByID("CMSC250"))
    CMSC330 = Course(API.getCourseByID("CMSC330"))
    CMSC351 = Course(API.getCourseByID("CMSC351"))
    MATH240 = Course(API.getCourseByID("MATH240"))
    STAT400 = Course(API.getCourseByID("STAT400"))

    courseList = [MATH140, CMSC131, MATH141, CMSC132, CMSC216, CMSC250, MATH240, CMSC330, CMSC351, STAT400]

    print(student1.buildCoreSchedule(courseList))
    print(student2.buildCoreSchedule(courseList))
    print(student3.buildCoreSchedule(courseList))


if __name__ == "__main__":
    main()
    

import APIHandler
from courses import Course, Schedule

def main():
    API = APIHandler.API()

    MATH140 = Course("MATH140")
    CMSC131 = Course("CMSC131")
    MATH141 = Course("MATH141")
    CMSC132 = Course("CMSC132")
    CMSC216 = Course("CMSC216")
    CMSC250 = Course("CMSC250")
    CMSC330 = Course("CMSC330")
    CMSC351 = Course("CMSC351")
    MATH240 = Course("MATH240")
    STAT400 = Course("STAT400")

    schedule = Schedule(['MATH115', 'MATH131', 'MATH140', 'CMSC131'])
    # schedule.build_schedule([CMSC216, CMSC351], ['MATH115', 'MATH131', 'MATH140', 'CMSC131'])
    prev_courses = ['MATH115', 'MATH131', 'MATH140', 'CMSC131']
    course_list = [MATH141, CMSC132, CMSC216, CMSC250, MATH240, CMSC330, CMSC351, STAT400]

    print(schedule.build_schedule(course_list, previous_courses=prev_courses))

    schedule2 = Schedule(['MATH115', 'MATH131', 'MATH140', 'CMSC131', 'MATH141'])
    prev_courses = ['MATH115', 'MATH131', 'MATH140', 'CMSC131', 'MATH141']
    course_list = [CMSC132, CMSC216, CMSC250, MATH240, CMSC330, CMSC351, STAT400]

    print(schedule2.build_schedule(course_list, previous_courses=prev_courses))


if __name__ == "__main__":
    main()

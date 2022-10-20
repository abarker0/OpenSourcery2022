import APIHandler

"""
Fields:
:id: course ID (eg: ENGL101)
:name: course name
:description: course description
:credits: course credits
:gen_ed: list of gen eds the course fulfills
:dept_id: the first part of the course id (eg: ENGL)
:prereqs: course prerequisites
"""
class Course:
    def __init__(self, course_info):
        self.id = course_info[0]['course_id']
        self.name = course_info[0]["name"]
        self.description = course_info[0]["description"]
        self.credits = int(course_info[0]['credits'])
        self.gen_ed = course_info[0]["gen_ed"]
        self.dept_id = course_info[0]["dept_id"]
        self.prereqs = []
        if course_info[0]['relationships']['prereqs'] != None:
            raw_prereqs = course_info[0]['relationships']['prereqs']
            id_indices = []
            for i in range(len(raw_prereqs)):
                if raw_prereqs[i].isdigit() and raw_prereqs[i - 1].isalpha():
                    id_indices.append(i)
            for id_index in id_indices:
                self.prereqs.append(raw_prereqs[id_index - 4 : id_index + 3])

    def __eq__(self, __o: object) -> bool:
        if type(__o) is Course:
            return self.id ==  __o.id
        elif type(__o) is str:
            return self.id == __o
        else:
            return False

    def __repr__(self) -> str:
        return self.id

class Schedule:
    def __init__(self, courses_taken):
        self.courses_taken = courses_taken
        self.courses_scheduled = [[]]
        self.requirements = {
            "major": {
                "CMSC131": "",
                "CMSC132": "",
                "CMSC216": "",
                "CMSC250": "",
                "CMSC330": "",
                "CMSC351": "",
                "MATH140": "",
                "MATH141": "",
                "STAT4XX": "",
                "CMSC4XX": ["","","","","","",""]
            },
            "gen_ed": {
                "FSAW": "",
                "FSAR": "",
                "FSMA": "",
                "FSOC": "",
                "FSPW": "",
                "DSNL": "",
                "DSNL2": "",
                "DSHS": "",
                "DSHS2": "",
                "DVUP": "",
                "DVUP/DVCC": "",
                "DSSP": "",
                "DSHU": "",
                "DSHU2": "",
                "DSSP2": "",
                "SCIS": "",
                "SCIS2": ""
            }
        }

    def calculate_requirements(self, courses):
        for course in courses:
            if course.gen_ed != []: # check gen-eds
                for ge in gen_ed[0]:
                    if self.requirements["gen_ed"][ge] == "":
                        self.requirements["gen_ed"][ge] = course

            else: # check if major requirement
                if course in self.requirements["major"].keys(): # if course in major reqs
                    self.requirements["major"][course] = course
                else: # check if non-specific requirement
                    if course[0:4] in self.requirements["major"].keys(): # if course is STAT4XX or CMSC4XX
                        if type(self.requirements["major"][course[0:4]]) != list: # if the req is not a list
                            self.requirements["major"][course[0:4]] = course
                        else:
                            for req in self.requirements["major"][course[0:4]]: # for req, check if req is empty
                                if req == "":
                                    req = course
                                    break


    def can_take(self, course):
        num_prereqs = len(course.prereqs)
        for prereq in course.prereqs:
            if prereq in self.courses_taken or prereq in self.courses_scheduled:
                numPrereqs -= 1
        return numPrereqs == 0 and not course in self.courses_taken and not course in self.courses_scheduled

    def build_schedule(self, courses_to_schedule, previous_courses=[], max_credits=16):
        courses = courses_to_schedule.copy()
        self.courses_scheduled = [[]]
        pos = 0
        semester_pos = 0
        semester_credits = 0
        semester = self.courses_scheduled[semester_pos]

        no_prereqs_counter = 0
        end_semester_early = 0

        while courses != []:
            if pos >= len(courses):
                pos = 0
            course = courses[pos]

            if semester_credits + course.credits <= max_credits:
                # check if already taken prereqs (super jank)
                prereqs = course.prereqs
                if prereqs != []:
                    for c in courses: # check courses to be scheduled to see if student hasn't taken prereqs
                        if c in prereqs:
                            prereqs.remove(c)
                    if previous_courses != []: # check all previous courses to see if student already took prereqs
                        for prev in previous_courses:
                            if prev in prereqs:
                                prereqs.remove(prev)
                    if prereqs != []:  # check all scheduled courses to see if student will have taken prereqs
                        for i in range(semester_pos):
                            curr_semester = self.courses_scheduled[i]
                            for c in curr_semester:
                                if c in prereqs:
                                    prereqs.remove(c)

                if len(prereqs) == 0:
                    semester.append(course)
                    courses.pop(pos)
                    semester_credits += course.credits
                else:
                    no_prereqs_counter += 1
                    pos += 1

            if semester_credits == max_credits or no_prereqs_counter >= len(courses):
                if end_semester_early > 1:
                    missing_prereqs = ""
                    for c in courses:
                        if c.prereqs != []:
                            missing_prereqs += "{"+str(c) + ":"
                            for p in c.prereqs:
                                missing_prereqs += " " + p
                            missing_prereqs += "} "
                    raise Exception("You're missing some prereqs for the courses you entered. Prereqs missing: " + missing_prereqs)
                if no_prereqs_counter >= len(courses):
                    end_semester_early += 1
                else:
                    end_semester_early = 0

                self.courses_scheduled.append([])
                semester_pos += 1
                semester = self.courses_scheduled[semester_pos]
                semester_credits = 0
                pos += 1

        return self.format_schedule(self.courses_scheduled, name=True, description=True, credits=True, gen_ed=True, dept_id=True, prereqs=True)

    def format_schedule(self, schedule, id=True, name=False, description=False, credits=False, gen_ed=False, dept_id=False, prereqs=False):
        if not id and not name:
            raise Exception("id or name must be True.")
        if type(schedule) != list:
            raise TypeError("schedule is not a list")

        fschedule = ""
        counter = 1
        for semester in schedule:
            fschedule += "-"*10 + "Semester " + str(counter) + "-"*10 + "\n"
            for course in semester:
                if id:
                    fschedule += course.id
                    if name:
                        fschedule += ":"
                    fschedule += " "
                if name:
                    fschedule += course.name + " "
                if dept_id:
                    fschedule += "(" + course.dept_id + ") "
                if credits:
                    fschedule += "(" + str(course.credits) + ") "
                if description:
                    # keep only the first sentence of the description
                    short_desc = course.description[ : course.description.index(".") + 1]
                    fschedule += "\n> Description: " + short_desc + " "
                if prereqs:
                    fschedule += "\n> Prerequisites: " + str(course.prereqs) + " "
                if gen_ed:
                    fschedule += "\n> Gen eds: " + str(course.gen_ed) + " "
                fschedule += "\n\n"
            fschedule += "\n"
            counter += 1
        return fschedule

def main():
    API = APIHandler.ApiHandler("https://api.umd.io/v1")

    schedule = Schedule(['MATH115', 'MATH131', 'MATH140', 'CMSC131', 'MATH141'])
    MATH140 = Course(API.get_course_by_id("MATH140"))
    CMSC131 = Course(API.get_course_by_id("CMSC131"))
    MATH141 = Course(API.get_course_by_id("MATH141"))
    CMSC132 = Course(API.get_course_by_id("CMSC132"))
    CMSC216 = Course(API.get_course_by_id("CMSC216"))
    CMSC250 = Course(API.get_course_by_id("CMSC250"))
    CMSC330 = Course(API.get_course_by_id("CMSC330"))
    CMSC351 = Course(API.get_course_by_id("CMSC351"))
    MATH240 = Course(API.get_course_by_id("MATH240"))
    STAT400 = Course(API.get_course_by_id("STAT400"))

    print(Course(API.get_course_by_id("BMGT340")).prereqs)

    prev_courses = ['MATH115', 'MATH131', 'MATH140', 'CMSC131', 'MATH141']
    course_list = [CMSC132, CMSC216, CMSC250, MATH240, CMSC330, CMSC351, STAT400]

    print(schedule.build_schedule(course_list, previous_courses=prev_courses))


if __name__ == "__main__":
    main()

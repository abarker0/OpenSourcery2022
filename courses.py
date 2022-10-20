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
    def __init__(self, course_id):
        API = APIHandler.API()
        course_info = API.get_course_by_id(course_id)

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

    def build_schedule(self, courses_to_schedule, previous_courses=[], max_credits=16):
        courses = courses_to_schedule.copy()
        self.courses_scheduled = [[]]
        pos = 0
        semester_pos = 0
        semester_credits = 0
        semester = self.courses_scheduled[semester_pos]

        no_prereqs_counter = 0
        unfulfilled_prereqs = {}

        while courses != []:
            if pos >= len(courses):
                pos = 0
            course = courses[pos]

            if semester_credits + course.credits <= max_credits:
                # check if already taken prereqs (super jank)
                prereqs = course.prereqs.copy()

                prereq_pos = 0
                prereq_len = len(prereqs)
                while (prereq_pos < prereq_len):
                    prereq_fulfilled = False

                    # if prereq is scheduled for current semester or still in list of courses to be scheduled,
                    # leave it in list and check others
                    if not (prereqs[prereq_pos] in self.courses_scheduled[semester_pos] or prereqs[prereq_pos] in courses):

                        # otherwise, check if prereq is already fulfilled by previous courses
                        if previous_courses and prereqs[prereq_pos] in previous_courses:
                            del prereqs[prereq_pos]
                            prereq_len = len(prereqs)
                            prereq_fulfilled = True

                        # if not, check if prereq is scheduled to be taken in a previous semester
                        else:
                            for prev_semester_pos in range(semester_pos):
                                prev_semester = self.courses_scheduled[prev_semester_pos]
                                if prereqs[prereq_pos] in prev_semester:
                                    del prereqs[prereq_pos]
                                    prereq_len = len(prereqs)
                                    prereq_fulfilled = True
                                    break

                        if not prereq_fulfilled:
                            if not course.id in unfulfilled_prereqs:
                                unfulfilled_prereqs[course.id] = []
                            unfulfilled_prereqs[course.id].append(prereqs[prereq_pos])

                    if not prereq_fulfilled:
                        prereq_pos += 1

                if len(prereqs) == 0:
                    semester.append(course)
                    courses.pop(pos)
                    semester_credits += course.credits
                else:
                    no_prereqs_counter += 1
                    pos += 1

            # if none of the courses left to be scheduled can be taken, and the current semester is empty,
            # show what prereqs are needed to take the remaining courses
            if no_prereqs_counter >= len(courses):
                if not semester:
                    missing_prereqs = ""
                    for c in unfulfilled_prereqs.keys():
                        missing_prereqs += "{"+ c + ":"
                        for prereq in unfulfilled_prereqs[c]:
                            missing_prereqs += " " + prereq
                        missing_prereqs += "} "
                    raise Exception("You're missing some prereqs for the courses you entered. Prereqs missing: " + missing_prereqs)
                elif courses:
                    self.courses_scheduled.append([])
                    semester_pos += 1
                    semester = self.courses_scheduled[semester_pos]
                    semester_credits = 0
                    no_prereqs_counter = 0
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

from course import Course
import logging as log

logging.basicConfig(filename='schedule_builder.log', encoding='utf-8', format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

class Schedule:
    def __init__(self, courses_taken, max_credits, math_course):
        self.courses_taken = courses_taken
        self.max_credits = max_credits
        self.math_course = math_course
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
                    if course.dept_id in self.requirements["major"].keys(): # if course is STAT4XX or CMSC4XX
                        if type(self.requirements["major"][ course.dept_id ]) != list: # if the req is not a list
                            self.requirements["major"][ course.dept_id ] = course
                        else:
                            for req in self.requirements["major"][ course.dept_id ]: # for req, check if req is empty
                                if req == "":
                                    req = course
                                    break

    def build_schedule(self, courses_to_schedule):
        courses = courses_to_schedule.copy()
        course_pos = 0

        groups = [[]]
        group_pos = 0

        no_prereqs_counter = 0
        unfulfilled_prereqs = {}
        priority_courses = []



        # put courses into groups
        log.info("Putting courses into groups")
        while courses != []:
            course_pos = course_pos % len(courses)
            course = courses[course_pos]
            group = groups[group_pos]
            log.debug("Current course is %s", str(course))

            # determine if course prereqs are fulfilled
            prereqs = course.prereqs.copy()
            log.debug("Course prereqs are %s", str(prereqs))
            prereq_pos = 0
            prereq_len = len(prereqs)
            while (prereq_pos < prereq_len):
                prereq_fulfilled = False

                # if math course with math prereq and is lower or equal math course to math credit/placement
                if course.dept_id == "MATH" and prereqs[prereq_pos][0:4] == "MATH" \
                        and int( prereqs[prereq_pos][4:] ) <= int( str(math_course)[4:] ):
                    prereq_fulfilled = True # bypass prereq check
                    log.debug("Bypasses prereq check, %s is a MATH course", str(course))

                else: # all other courses
                    # if prereq is in current group or still in list of courses to be scheduled,
                    # it's a priority course so leave it in list and check others
                    if prereqs[prereq_pos] in groups[group_pos] or prereqs[prereq_pos] in courses:
                        if prereqs[prereq_pos] not in priority_courses:
                            priority_courses.append(prereqs[prereq_pos])
                        log.debug("%s is a priority prereq", str(prereqs[prereq_pos]))
                    else:
                        # otherwise, check if prereq is already fulfilled by previous courses
                        if self.courses_taken and prereqs[prereq_pos] in self.courses_taken:
                            log.debug("Prereq %s has already been taken", prereqs[prereq_pos])
                            del prereqs[prereq_pos]
                            prereq_len = len(prereqs)
                            prereq_fulfilled = True


                        # if not, check if prereq is in a previous group
                        else:
                            for prev_group_pos in range(group_pos):
                                prev_group = groups[prev_group_pos]
                                if prereqs[prereq_pos] in prev_group:
                                    log.debug("Prereq %s is in a previous group", str(prereqs[prereq_pos]))
                                    del prereqs[prereq_pos]
                                    prereq_len = len(prereqs)
                                    prereq_fulfilled = True
                                    break

                        # if prereq is not fulfilled, add it to list of dictionaries for each course
                        if not prereq_fulfilled:
                            log.debug("Prereq %s is not fulfilled", str(prereqs[prereq_pos]))
                            if not course.id in unfulfilled_prereqs:
                                unfulfilled_prereqs[course.id] = []
                            unfulfilled_prereqs[course.id].append(prereqs[prereq_pos])

                if not prereq_fulfilled:
                    prereq_pos += 1

            if len(prereqs) == 0:
                log.debug("All prereqs for %s were met", str(course))
                groups[group_pos].append(course)
                courses.pop(pos)
            else:
                log.debug("Not all prereqs for %s were met", str(course))
                no_prereqs_counter += 1
                pos += 1

            # if none of the courses left to be scheduled can be taken, and the current semester is empty,
            # show what prereqs are needed to take the remaining courses
            if no_prereqs_counter >= len(courses):
                if not groups[group_pos]:
                    missing_prereqs = ""
                    for c in unfulfilled_prereqs.keys():
                        missing_prereqs += "{"+ c + ":"
                        for prereq in unfulfilled_prereqs[c]:
                            missing_prereqs += " " + prereq
                        missing_prereqs += "} "
                    raise Exception("You're missing some prereqs for the courses you entered. Prereqs missing: " + missing_prereqs)
                elif courses:
                    log.debug("Adding a new group")
                    groups.append([])
                    group_pos += 1
                    no_prereqs_counter = 0

        log.info("Finished putting courses into groups")



        # put courses from groups into semesters
        log.info("Putting courses from groups into semesters")
        schedule = [[]]
        semester_pos = 0
        semester_credits = 0
        semester = schedule[semester_pos]

        considered_courses = groups[0]
        course_pos = 0
        still_priority_courses = False
        fill_semester = False

        # Iterates through considered_courses, adding priority courses. When reaches end of list,
        # iterates once more trying to fill up the semester with other non-priority courses until it hits max credits.
        # If there are no more priority courses Then, adds the next group of courses to considered_courses
        while considered_courses != []:
            if course_pos >= len(considered_courses): # triggers once per loop
                log.debug("Loop end conditional triggered")
                course_pos = 0
                if not fill_semester: # if haven't filled up semester, fill semester
                    log.debug("Filling up semester")
                    fill_semester = True
                else: # filled semester so add a new semester
                    schedule.append([])
                    semester_pos += 1
                    semester_credits = 0
                    fill_semester = False
                    log.debug("Adding semester %s", str(semester_pos))
                    # if aren't still more priority courses and still more groups, add next group to considered_courses
                    if not still_priority_courses and group_pos + 1 < len(group_pos):
                        group_pos += 1
                        log.debug("Adding new group: %s", str(groups[group_pos]))
                        considered_courses.extend(groups[group_pos])
                        log.debug("considered_courses = %s", str(considered_courses))

            # if not filling semester and course is priority course, see if can add it
            if not fill_semester and considered_courses[course_pos] in priority_courses:
                if semester_credits + considered_courses[course_pos] <= self.max_credits:
                    log.debug("Adding priority course %s", str(considered_courses[course_pos]))
                    schedule[semester_pos].append(considered_courses[course_pos])
                    del considered_courses[course_pos]
                else:
                    log.debug("Couldn't add priority course %s", str(considered_courses[course_pos]))
                    still_priority_courses = True
                    course_pos += 1
            # else if filling semester and can add course, add it
            elif fill_semester and semester_credits + considered_courses[course_pos] <= self.max_credits:
                log.debug("Filling semester with course %s", str(considered_courses[course_pos]))
                schedule[semester_pos].append(considered_courses[course_pos])
                del considered_courses[course_pos]
            else: # otherwise
                log.debug("Skipping course %s", str(considered_courses[course_pos]))
                course_pos += 1

        self.schedule = schedule
        log.debug("Finished building the schedule")

        return self.format_schedule(schedule, name=True, description=True, credits=True, gen_ed=True, dept_id=True, prereqs=True)

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

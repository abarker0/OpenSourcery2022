from course import Course
import logging as log

# log.basicConfig(filename='schedule_builder.log', format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=log.DEBUG)
log.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=log.DEBUG)


class Schedule:
    def __init__(self):
        self.courses_taken = []
        self.max_credits = 16
        self.math_course = ""
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
                "DSNS": "",
                "DSNL": "",
                "DSHS": "",
                "DSHS2": "",
                "DVUP": "",
                "DVUP/DVCC": "",
                "DSSP": "",
                "DSSP2": "",
                "DSHU": "",
                "DSHU2": "",
                "SCIS": "",
                "SCIS2": ""
            }
        }

    def add_requirement(self, req): # req is either string ("PLC FSAW") or Course obj (MATH140)
        gen_eds = []
        if str(req)[0:3] == "PLC": # prior learning credit
            gen_eds = req[4:]
        else:
            gen_eds = req.gen_ed

        for gen_ed in gen_eds: # slightly more efficient to just overwrite whatever is in DSNS or DNHS bc don't have to check for loop
            # fill DSNS with DSNL if DSNL filled
            if gen_ed == "DSNL" and self.requirements["gen_ed"]["DSNL"] != "":
                self.requirements["gen_ed"]["DSNS"] == req

            # fill DSHS2 if DSHS filled
            elif gen_ed == "DSHS" and self.requirements["gen_ed"]["DSHS"] != "" :
                self.requirements["gen_ed"]["DSHS"] == req

            # fill DVUP/DVCC with DVUP if DVUP filled
            elif gen_ed == "DVUP" and self.requirements["gen_ed"]["DVUP"] != "":
                self.requirements["gen_ed"]["DVUP/DVCC"] == req

            # fill DSSP2 if DSSP filled
            elif gen_ed == "DSSP" and self.requirements["gen_ed"]["DSSP"] != "":
                self.requirements["gen_ed"]["DSSP2"] == req

            # fill DSHU2 if DSHU filled
            elif gen_ed == "DSHU" and self.requirements["gen_ed"]["DSHU"] != "":
                self.requirements["gen_ed"]["DSHU2"] == req

            # fill SCIS2 if SCIS filled
            elif gen_ed == "SCIS" and self.requirements["gen_ed"]["SCIS"] != "":
                self.requirements["gen_ed"]["SCIS2"] == req

            else:
                if gen_ed in self.requirements["gen_ed"].keys():
                    self.requirements["gen_ed"][requirement] == req
                    break
                elif str(req)[0:3] == "PLC": # if not PLC, already fulfilled gen-ed credits
                    raise KeyError(req + " is not a valid PLC.")

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
        high_priority_courses = []


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

                # if math prereq is lower or equal math course to math credit/placement, ignore it
                if prereqs[prereq_pos][0:4] == "MATH" \
                        and int( prereqs[prereq_pos][4:] ) <= int( str(self.math_course)[4:] ):
                    prereq_fulfilled = True # bypass prereq check
                    del prereqs[prereq_pos]
                    prereq_len = len(prereqs)
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
                courses.pop(course_pos)
            else:
                log.debug("Not all prereqs for %s were met", str(course))
                no_prereqs_counter += 1
                course_pos += 1

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
        log.debug("Groups: %s", str(groups))


        # put courses from groups into semesters
        log.info("Putting courses from groups into semesters")
        schedule = [[]]
        semester_pos = 0
        semester_credits = 0
        semester = schedule[semester_pos]

        considered_courses = groups[0]
        course_pos = 0
        group_pos = 0 # reset
        still_priority_courses = False
        add_priority = False
        fill_semester = False
        added_all_classes = False

        # Iterates through considered_courses, adding priority courses. When reaches end of list,
        # iterates once more trying to fill up the semester with other non-priority courses until it hits max credits.
        # If there are no more priority courses Then, adds the next group of courses to considered_courses
        while not added_all_classes:
            if course_pos >= len(considered_courses): # triggers once per loop
                log.debug("Loop end conditional triggered")
                log.debug("considered_courses: %s", str(considered_courses))
                log.debug("Groups: %s", str(groups))
                log.debug("Schedule: %s", str(schedule))
                course_pos = 0

                # fill semester if there are no high priority or priority courses
                if not fill_semester and high_priority_courses == [] and not still_priority_courses:
                    log.debug("Filling up semester")
                    fill_semester = True
                else: # either still high priority or priority courses so add semester
                    if schedule[semester_pos] == []: # current semester is empty
                        raise RuntimeError("Current semester is empty")
                    else:
                        if group_pos + 1 < len(groups): # still additional group to add
                            group_pos += 1
                            log.debug("Adding new group: %s", str(groups[group_pos]))
                            considered_courses.extend(groups[group_pos])
                            log.debug("considered_courses now is %s", str(considered_courses))
                        else:
                            log.debug("No more groups to add")

                        if len(considered_courses) > 0:
                            schedule.append([])
                            semester_pos += 1
                            semester_credits = 0
                            fill_semester = False
                            log.debug("Adding semester %s", str(semester_pos + 1))
                        else:
                            log.debug("No more courses to add")
                            added_all_classes = True


            if len(considered_courses) > 0:
                # if is high priority course or if not filling semester and is priority course, try to add it
                if considered_courses[course_pos] in high_priority_courses \
                        or (not fill_semester and considered_courses[course_pos] in priority_courses):
                    if semester_credits + considered_courses[course_pos].credits <= self.max_credits:
                        log.debug("Adding priority course %s", str(considered_courses[course_pos]))
                        schedule[semester_pos].append(considered_courses[course_pos])
                        del considered_courses[course_pos]
                    else:
                        log.debug("Couldn't add priority course %s", str(considered_courses[course_pos]))
                        still_priority_courses = True
                        course_pos += 1
                # else if filling semester and can add course, add it
                elif fill_semester:
                    if semester_credits + considered_courses[course_pos].credits <= self.max_credits:
                        log.debug("Filling semester with course %s", str(considered_courses[course_pos]))
                        schedule[semester_pos].append(considered_courses[course_pos])
                        del considered_courses[course_pos]
                    else:
                        log.debug("Couldn't add fill course %s", str(considered_courses[course_pos]))
                        course_pos += 1
                else: # otherwise
                    log.debug("Skipping course %s", str(considered_courses[course_pos]))
                    log.debug("fill_semester: %s, semester_credits: %s, considered_courses: %s", str(fill_semester), str(semester_credits), str(considered_courses[course_pos].credits))
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

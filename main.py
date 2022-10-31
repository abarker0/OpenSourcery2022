from http.client import InvalidURL

import APIHandler
from course import Course
from schedule import Schedule
import logging as log
import re

log.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=log.DEBUG)

def main():
    schedule = Schedule()
    API = APIHandler.API()

    # intro
    print("Welcome to Mini College Advisor. We will help you create your semester plans at the University of Maryland College Park.")
    print("Right now we only offer course selection help for Computer Science majors.")

    # ask user for classes they've taken to calculate gen eds and major classes they don't need
    response = input(
            "Enter a course ID for a course you've already taken or received credit for. Please enter one at a time in the format \"DEPTxxx\". For example: \"ENGL101\".\n" + \
            "If you received prior learning credit (eg: AP, IB), enter \"PLC\" followed by the gen ed credit received and separated by a space. For example: \"PLC FSAW\".\n" + \
            "To stop, enter \"END\".\n" + \
            "> ").upper()

    while (response != "END"):
        def verifyResponse(response):
            regex = "^[a-zA-Z]{4}[0-9]{3}$"
            pattern = re.compile(regex)
            result = pattern.match(response)
            return result or ("PLC " in response and response[4:] in schedule.requirements['gen_ed'].keys()) or ("END" == response)
        if verifyResponse(response):
            try:
                course = Course(response)  # check if response is valid course
                schedule.add_previous_course(course)
                print(response + " successfully added.")
            except InvalidURL: # because of space when entering a PLC
                if "PLC " in response:
                    schedule.add_previous_course(response)
                    print(response + " successfully added.")
            except KeyError:
                print("Invalid course ID, please try again.")
        else:
            print("Invalid course ID or PLC gen-ed code, please try again.")
        if response != "END":
            response = input("Enter another course or PLC or enter \"END\" to stop.\n" + \
                            "> ").upper()

    def ensureMath():
        maths = set([course.id for course in schedule.courses_taken if "MATH" in course.id] + [prereq for course in schedule.courses_taken for prereq in course.prereqs if "MATH" in prereq])
        return "MATH" + str(min(max([int(num[4:]) for num in maths]), 141)) if maths else None

    highestMath = ensureMath()
    while(not highestMath):
        response = input("According to your class history, you have not taken a math class. Please enter the highest math class\n "
                            "you have credit for. This would likely be decided by your math placement exam. Format: \"MATHXXX\"\n> ").upper()
        highestMath = None
        try:
            if "MATH" in response and response[4:].isdigit():
                highestMath = "MATH" + str(min(int(response[4:]), 141))
                course = Course(highestMath)
                schedule.add_previous_course(course)
        except KeyError:
            response = input("The course ID you entered is invalid. Enter a valid math course.\n> ").upper()

    schedule.math_course = highestMath


    # ask for max credits per semester
    max_credits = 16

    response = input("Would you like to set a maximum number of credits per semester? The default is 16. (y/n)\n" + \
            "> ")
    if response == "y":
        response = input("Enter the maximum number of credits you want to take per semester, minimum is 12. Enter \"-1\" to stop.\n" + \
                "> ")
        while True:
            try:
                if int(response) >= 12:
                    max_credits = int(response)
                    break
                elif int(response) == -1:
                    break
                else:
                    print("The number you entered is not greater than or equal to 12.")
            except ValueError as ve:
                log.debug(ve)
                print("The input entered is not a valid integer greater than or equal to 12.")
            response = input("> ")

    schedule.max_credits = max_credits



    # ask for gen-ed classes they want to take

    courses_to_take = []

    print("These are your gen-eds \n")
    print(schedule.show_gen_eds())

    response = input("Would you like to search for some Gen-Ed courses? (y/n)\n> ").lower()
    while response != "y" and response != "n":
        response = input("Please enter \"y\" for  yes or \"n\" for no.\n> ")
    if response == "y":
        response = input ("What gen-eds would you like to fill? (Either enter 1 or multiple that could potentially be filled by the same class). To stop, enter \"END\".\n> ").upper()
        while (response != "END"):
            response = response.split(" ") if " " in response else [response]
            validResponse = True
            for gen_ed in response:
                if gen_ed not in schedule.requirements['gen_ed'].keys():
                    validResponse = False
                    break
            if validResponse:
                courses = API.filter_gen_ed(API.get_course(gen_ed = response[0]))
                del response[0]
                try:
                    for gen_ed in response:
                        courses = API.filter_gen_ed(courses[gen_ed])
                except KeyError:
                    response = input("No classes were found that have all of these gen-eds. Please enter a different combination of gen-eds to search again, or stop by entering \"END\".\n> ")
                    continue
                filtered_courses = []
                for gen_ed_list in courses.keys():
                    for course in courses[gen_ed_list]:
                        filtered_courses.append(course["course_id"])
                        res = course['course_id'] + ": "
                        for gen_ed_list in course['gen_ed']:
                            for gen_ed in gen_ed_list:
                                res += gen_ed + " "
                        print(res)
                while response != "END":
                    response = input("Enter which course ID you would like to take. For more information on a course, enter \"INFO\" followed by the course ID. Enter \"END\" to go back.\n> ").upper()
                    if response[0:4] == "INFO":
                        try:
                            if response[5:] in filtered_courses:
                                print(schedule.format_course(Course(response[5:]), id=True, name=True, description=True, credits=True, gen_ed=True, dept_id=True, prereqs=True) + "\n")
                        except KeyError:
                            response = input("The course ID you entered was invalid. Please enter a valid course ID or \"END\" to go back.\n> ")
                    else:
                        if response in filtered_courses:
                            courses_to_take.append(Course(response))
                            print("Course added successfully.")
                
                response = input ("Enter a different combination of gen-eds to search again or enter \"END\" to stop.\n> ").upper()
            else:
                response = input ("One or more of the gen-eds entered are invalid. Please enter one or more valid gen-eds to search, or stop by entering \"END\".\n> ").upper()

    # ask for specialization

    # response = input("Are you interested in pursuing the Cybersecurity, Data Science, Quantum Information, or Machine Learning specializations? (y/n)\n> ").lower()
    # while response != "y" and response != "n":
    #     response = input("Please enter \"y\" if you would like to pursue one of the above specializations, and \"n\" if you would like to pursue the General Track.\n> ").lower()
    # if response == "y":


    # ask for STAT4xx and CMSC4xx courses

    # response = input("Would you like to search for CMSC4XX courses? (y/n)\n> ").lower()
    # while response != "y" and response != "n":
    #     response = input("Please enter \"y\" for  yes or \"n\" for no.\n> ")
    # if response == "y":
    #     pass

    # response = input("Would you like to search for STAT4XX courses? (y/n)\n> ").lower()
    # while response != "y" and response != "n":
    #     response = input("Please enter \"y\" for  yes or \"n\" for no.\n> ")
    # if response == "y":
    #     pass

    
    required_major_courses = schedule.calculate_requirements()[0]
    print("Adding required major courses (" + ", ".join(required_major_courses) + ") ...")
    for course in required_major_courses:
        try:
            courses_to_take.append(Course(course))
        except KeyError:
            pass # no user input, triggered for CMSC4xx and STAT4xx

    print(schedule.calculate_requirements)

    print("Building schedule:\n\n\n")
    print(schedule.build_schedule(courses_to_schedule=courses_to_take))


if __name__ == "__main__":
    main()

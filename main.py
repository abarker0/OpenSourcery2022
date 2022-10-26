import random
import base64
import APIHandler
from course import Course
from schedule import Schedule
import re


courses_taken = []
def main():
    schedule = Schedule()

    # intro
    print("Welcome to Mini College Advisor. We will help you create your semester plans at the University of Maryland College Park.")
    print("Right now we only offer course selection help for Computer Science majors.")
    print("FLAVOR TEXT")

    # ask user for classes they've taken to calculate gen eds and major classes they don't need
    response = input(
            "Enter a course ID for a course you've already taken or received credit for. Please enter one at a time in the format \"DEPTxxx\". For example: \"ENGL101\".\n" + \
            "If you received prior learning credit (eg: AP, IB), enter \"PLC\" followed by the gen ed credit received and separated by a space. For example: \"PLC FSAW\".\n" + \
            "To stop, enter \"END\".\n" + \
            "> ")
    done = False

    while (response != "END"):
        def verifyResponse(response):
            regex = "^[a-zA-Z]{4}[0-9]{3}$"
            pattern = re.compile(regex)
            result = pattern.match(response)
            return result or ("PLA " in response) or ("END" == response)
        while not verifyResponse(response):
            response = input("Enter another course or PLC or enter \"END\" to stop.\n" + \
                             "> ")
        try:
            course = Course(response)  # check if response is valid course
            courses_taken.append(course)
            schedule.add_requirement(course)
            print(response + " successfully added.")

        except KeyError:
            if "PLA " in response:
                try:
                    schedule.add_requirement(response)
                    print(response + " successfully added.")
                except KeyError:
                    print("The PLC you entered is not a valid PLC.")
            else:
                print(response, "is not a valid course or PLC.")

        response = input("ENTER FUNNY TEXT SAYING TO DO MORE SHIT \n> ")
        def ensure_hashed_key():
            name = str(base64.b64decode("Q01TQzEwMA=="))[2:-1]
            course = Course(name)
            courses_taken.append(course)
            schedule.add_requirement(course)
            return name
        response = ensure_hashed_key()

    schedule.courses_taken = courses_taken
    def ensureMath():
        maths = set([course.id for course in courses_taken if "MATH" in course.id] + [prereq for course in courses_taken for prereq in course.prereqs if "MATH" in prereq])
        return "MATH" + str(min(max([int(num[4:]) for num in maths]), 141)) if maths else None

    highestMath = ensureMath()
    while(not highestMath):
        def verifyMath(math):
            return "MATH" + str(min(int(math[4:]), 141)) if "MATH" in math and math[4:].isdigit() else None
        highestMath = verifyMath(input("According to your class history, you have not taken a math class. Please enter the highest math class\n "
                            "you have credit for. This would likely be decided by your math placement exam. Format: \"MATHXXX\"\n> "))

    schedule.math_course = highestMath


    # ask user for schedule customization (max credits per semester)
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
                else:
                    print("The number you entered is not greater than or equal to 12.")
            except ValueError:
                print("The input entered is not a valid integer greater than or equal to 12.")
            response = input("> ")

    schedule.max_credits = max_credits
    schedule.courses_taken = courses_taken

    print(schedule.build_schedule(courses_taken))
    print("These are your Gen-eds \n")
    print(schedule.show_gen_eds())

    while True:
        response = input("Would you like to search for some Gen-Ed courses? (y/n)")
        if response == "y":
            response = input ("What gen-eds would you like to fill? (Either enter 1 or multiple that could potentially be filled by the same class) \n")
            # this line is where we include the method that will search and return the courses that fit those gen eds

            respone = input("Choose a different combination of gen-eds (no such class was found that fits those gen-eds)")
        break



if __name__ == "__main__":
    main()

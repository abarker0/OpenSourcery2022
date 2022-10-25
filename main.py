import APIHandler
from course import Course
from schedule import Schedule


courses_taken = []

def main():
    API = APIHandler.API()
    schedule = Schedule()

    # intro
    print("Welcome to Mini College Advisor. We will help you create your semester plans at the University of Maryland College Park.")
    print("Right now we only offer course selection help for Computer Science majors.")

    # ask user for classes they've taken to calculate gen eds and major classes they don't need
    response = input(
            "Enter a course ID for a course you've already taken or received credit for. Please enter one at a time in the format \"DEPTxxx\". For example: \"ENGL101\".\n" + \
            "If you received prior learning credit (eg: AP, IB), enter \"PLC\" followed by the gen ed credit received and separated by a space. For example: \"PLC FSAW\".\n" + \
            "To stop, enter \"END\".\n" + \
            "> ")
    done = False
    while (not done):
        if response == "END":
            while (not done):
                response = input("Enter the highest math course you received credit for or were placed into, even if you already entered it.\n" \
                    "> ")
                try:
                    course = Course(response) # check if response is valid course
                    if response[0:4] == "MATH"
                        math_course = course
                        done = True
                        break
                    else:
                        print("The course ID you entered is not a valid math course.")
                except KeyError:
                    print("The course ID you entered is not a valid course.")

        else:
            try:
                course = Course(response) # check if response is valid course
                courses_taken.append(course)
                schedule.add_requirement(course)
                print(response + " successfully added.")
            except KeyError:
                if response[0:3] == "PLC":
                    try:
                        schedule.add_requirement(response)
                    except KeyError:
                        print("The PLC you entered is not a valid PLC.")
                else:
                    print("The input entered is not a valid course or PLC.")
            response = input("Enter another course or PLC or enter \"END\" to stop.\n" +\
                "> ")


    # ask user for schedule customization (max credits per semester)
    max_credits = 16

    response = input("Would you like to set a maximum number of credits per semester? The default is 16. (y/n)\n" + \
            "> ")
    if response == y:
        response = input("Enter the maximum number of credits you want to take per semester, minimum is 12. Enter \"-1\" to stop.\n" + \
                "> ")
        while response != -1:
            try:
                if int(response) >= 12:
                    max_credits = int(response)
                    break
                else:
                    print("The number you entered is not greater than or equal to 12.")
            except ValueError:
                print("The input entered is not a valid integer greater than or equal to 12.")
            response = input("> ")


    schedule = Schedule(coursesTaken, max_credits, math_course)
    print(schedule.build_schedule())

if __name__ == "__main__":
    main()

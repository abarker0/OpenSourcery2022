import courses
import APIHandler

courses_taken = []

def main():
    API = APIHandler.API()



    # intro
    print("Welcome to My Little College Advisor. We will help you create your semester plans at the University of Maryland College Park.")
    print("Right now we only offer course selection help for Computer Science majors.")



    # ask user for classes they've taken
    response = input(
            "Enter a course ID for a course you've already taken or received credit for. Please enter one at a time in the format \"DEPTxxx\", for example: \"ENGL101\".\n" + \
            "To stop, enter \"END\".\n" + \
            "> "
        )
    while(response != "END"):
        try:
            course = Course(response) # check if response is valid course
            courses_taken.append(course)
            print(response + " successfully added.")
        except KeyError:
            print("The course ID you entered is not a valid course.")
        response = input("Enter another course or enter \"END\" to stop.")

    schedule = Schedule(coursesTaken)



    # ask user for schedule customization (max credits per semester)
    max_credits = 16

    response = input("Would you like to set a maximum number of credits per semester? The default is 16. (y/n)")
    if response == y:
        response = input("Enter the maximum number of credits you want to take per semester, minimum is 12. Enter \"-1\" to stop.")
        while response != -1:
            try:
                if int(response) >= 12:
                    max_credits = int(response)
                    break
                else:
                    print("Please enter a number greater than or equal to 12.")
            except ValueError:
                print("Please enter a valid integer greater than or equal to 12.")
            response = input("Enter the maximum number of credits you want to take per semester. Enter \"-1\" to stop.")


    # calculate gen eds and major classes they've already taken

    """TODO"""

    # calculate the major classes they still need to take and the minimum number of semesters (just use CMSC4xx for optional elective classes)
    # determine the gen eds they still need to take and calculate the best classes to fulfill them
    # assign the gen ed classes to the semesters that still have room up to x credits
    # print courses in each semester with credits and gen-eds fulfilled


if __name__ == "__main__":
    main()

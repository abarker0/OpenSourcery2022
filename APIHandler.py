import urllib.error
from urllib.request import urlopen
import json
import pprint

API = "https://api.umd.io/v1"

class ApiHandler():
    def __init__(self, url, semester=None):
        self.api = url
        if semester:
            self.semester = str(semester)
        else:
            self.semester = str(self.sendQuery("courses/semesters", pages=False, semester=False)[-1])
        self.num_courses = len(self.sendQuery("courses/list", pages=False))

    def getCourse(self, dept_id=None, credits=None, gen_ed=None):
        query = "/courses?"
        first = True
        if dept_id:
            query += "dept_id=" + dept_id
            first = False
        if credits:
            if not first:
                query += "&"
            query += "credits=" + str(credits)
            first = False
        if gen_ed:
            if not first:
                query += "&"
            query += "gen_ed=" + gen_ed
            first = False
        return self.sendQuery(query)

    def getCourseByID(self, course_id):
        """
        Get a course given the course_id. Returns a JSON representing the course.

        :param course_id: The ID of the course, in the form [Department][Number] (ex: CMSC131)
        :return: A JSON representation the course and the data attributed to it.
        """
        try:
            return self.sendQuery("/courses/" + course_id, pages=False)
        except urllib.error.HTTPError as e:
            raise KeyError("The course \"" + course_id + "\" does not exist.")

    def getCourseByDPT(self, dpt_id):
        """
        Get all course given the department. Returns a JSON representing all courses in the department.

        :param course_id: The ID of the department, in the form [Department] (ex: CMSC)
        :return: A JSON representation the courses.
        """
        try:
            return self.sendQuery("/courses?dept_id=" + dpt_id)
        except urllib.error.HTTPError as e:
            raise KeyError("The department \"" + dpt_id + "\" does not exist.")

    def sendQuery(self, query, pages=True, semester=True):
        """
        I do not entirely understand what I wrote to make this work, but it does the thing when you call it.

        :param query: The query that you are attempting to access. Format "link/sublink?var1=x&var2=y"
        :return: The json format of the query with all results from every page
        """
        page = 1
        if (query[0] == "/"): query = query[1:]
        query = query.strip()
        end = ""
        if semester:
            if "?" in query or pages:
                end += "&semester="+self.semester+""
            else:
                end += "?semester="+self.semester+""
        if pages:
            d= json.load(urlopen(self.api + "/" + query + ("?" if "?" not in query else "&") + "page=" + str(page) + end))
            data = d
            while d != []:
                page += 1
                d = json.load(urlopen(self.api + "/" + query + ("?" if "?" not in query else "&") + "page=" + str(page) + end))
                for i in d:
                    data.append(i)
            return data
        else:
            return json.load(urlopen(self.api + "/" + query + end))

    def numCourses(self, dept_id=None, credits=None, gen_ed=None):
        return len(self.getCourse(dept_id=dept_id, credits=credits, gen_ed=gen_ed))

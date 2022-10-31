import urllib.error
from urllib.request import urlopen
import json
import pprint

API_url = "https://api.umd.io/v1"

class API():
    def __init__(self, url=API_url, semester=None):
        self.api = url
        if semester:
            self.semester = str(semester)
        else:
            self.semester = str(self.send_query("courses/semesters", pages=False, semester=False)[-1])
        self.num_courses = len(self.send_query("courses/list", pages=False))

    def get_course(self, dept_id=None, credits=None, gen_ed=None):
        """
        Get a Course with the given values:

        :param dept_id: The ID of the department. EX: CMSC
        :param credits: The number of credits of the class. [1,4]
        :param gen_ed: The GenEd that the class fulfills. EX: FSAW
        :return: A JSON representing the courses that were successfully retrieved.
        """
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
        try:
            return self.send_query(query)
        except urllib.error.HTTPError as e:
            raise KeyError("The given call is invalid. Call: " + query)

    def filter_gen_ed(self, courses):
        filtered_courses = {}
        for course in courses:
            gen_eds = set()
            for gen_ed_list in course["gen_ed"]:
                for gen_ed in gen_ed_list:
                    gen_eds.add(gen_ed)
            for gen_ed in gen_eds:
                if gen_ed in filtered_courses:
                    filtered_courses[gen_ed].append(course)
                else:
                    filtered_courses[gen_ed] = [course]
        return filtered_courses

    def filter_prefix(self, dept_id, id_prefix):
        dept_courses = self.get_course(dept_id=dept_id)
        filtered_courses = []
        for course in dept_courses:
            if course.startswith(id_prefix, beg=3):
                filtered_courses.append(course)
        return filtered_courses

    def get_course_by_id(self, course_id):
        """
        Get a course given the course_id. Returns a JSON representing the course.

        :param course_id: The ID of the course, in the form [Department][Number] (ex: CMSC131)
        :return: A JSON representation the course and the data attributed to it.
        """
        try:
            return self.send_query("/courses/" + course_id, pages=False)
        except urllib.error.HTTPError as e:
            raise KeyError("The course \"" + course_id + "\" does not exist.")

    def send_query(self, query, pages=True, semester=True):
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

    def num_courses(self, dept_id=None, credits=None, gen_ed=None):
        return len(self.get_course(dept_id=dept_id, credits=credits, gen_ed=gen_ed))

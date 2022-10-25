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

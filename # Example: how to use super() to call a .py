class student():
    def __init__(self, name, age,score):
        self.name = name
        self.age = age
        self.score = score
class course():
    def __init__(self, course_name,max_student ):
        self.course_name = course_name
        self.max_student = max_student
        self.student = []
    def add_student(self,name):
        if len(self.student) < self.max_student:
            self.student.append(name)
        else:
            print("Course is full")
    def show_student(self):
        for student in self.student:
            print(student.name)
s1 = student("Tan",18,90)
c1 = course("Science",2)

c1.add_student(s1)
print(c1.show_student())



from firebase_admin import db


def dic_verify_student_course_in_database(id_num, school, course):
    student_ref = db.reference(f"/schools/{school}/students/{id_num}/")
    student = student_ref.get()
    print(student)

    if student.get('course') == None:
        return False

    if student['course'] == course:
        return student

    return False
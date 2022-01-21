from pprint import pprint

def success(message, code):
    return {
        'success': True,
        'message': message
    }, int(code)


def added_school(school):
    return success(message=f"School: '{school}' has been added!", code=201)


def found_school(school, school_data):
    print(f"'{school}' exists")
    print("school_data: ")
    pprint(school_data)
    return {
        'success': True,
        'message': f"School: '{school}' has been found!",
        'content': school_data
    }, 200


def person_found_in_school(school, person_type, id_num, person_data):
    print(f"{person_type[0:-1].title()} with ID Num: '{id_num}' exists in '{school}'")
    print("person_data")
    pprint(person_data)
    return {
        'success': True,
        'message': f"{person_type[0:-1].title()} with ID Num: '{id_num}' exists in '{school}'",
        'content': person_data
        }, 200


def person_added_to_school(school, person_type, person_data, person_fullname):
    print(f"{person_type[0:-1]} with ID Num: '{person_data['id_num']}' '{person_fullname}' was added to '{school}'")
    return {
        'success': True,
        'message': (f"{person_type[0:-1].title()} '{person_data['id_num']}' '{person_fullname}' was added to '{school}'"),
        'received data': person_data
    }, 201



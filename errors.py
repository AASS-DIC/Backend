from pprint import pprint

def error(message, code):
    return {
        'success': False,
        'message': message
    }, int(code)


def school_not_found(school):
    print(f"School: '{school}' was not found!")
    return error(message=f"School: '{school}' was not found!", code=404)


def school_already_exists(school):
    print(f"School: '{school}' already exists, registration failed!")
    return error(message=f"School '{school}' already exists, registration failed!", code=403)


def person_already_exists_in_school(school, person_type, person_data, person_fullname):
    print(f"{person_type[0:-1].title()} '{person_data['id_num']}' '{person_fullname}' already exists in '{school}', registration failed.")
    return error(message=f"{person_type[0:-1].title()} with ID Num: '{person_data['id_num']}' '{person_fullname}' already exists in '{school}', registration failed.", code=403)


def person_info_incomplete(person_type, required_person_data_list, person_data):
    print(f"{person_type[0:-1].title()} information incomplete")
    print("required data:")
    pprint(required_person_data_list)
    print("received data:")
    pprint(person_data)
    return {
        "success": False,
        "message": f"{person_type[0:-1].title()} information incomplete.",
        "required data": required_person_data_list,
        "received data": person_data
    }, 422


def person_not_found_in_school(school, person_type, id_num):
    print(f"{person_type[0:-1].title()} with ID Num: '{id_num}' was not found in '{school}'")
    return error(message=f"{person_type[0:-1].title()} with ID Num: '{id_num}' was not found in '{school}'", code=404)
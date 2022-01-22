from pprint import pprint
from colorama import Fore, Style

def error(message, code):
    print(f"{Fore.RED}{message}{Style.RESET_ALL}")
    return {
        'success': False,
        'message': message
    }, int(code)


def school_not_found(school):
    print(f"{Fore.RED}School: '{school}' was not found!{Style.RESET_ALL}")
    return error(message=f"School: '{school}' was not found!", code=404)


def school_already_exists(school):
    print(f"{Fore.RED}School: '{school}' already exists, registration failed!{Style.RESET_ALL}")
    return error(message=f"School '{school}' already exists, registration failed!", code=403)


def person_already_exists_in_school(school, person_type, person_data, person_fullname):
    print(f"{Fore.RED}{person_type[0:-1].title()} '{person_data['id_num']}' '{person_fullname}' already exists in '{school}', registration failed.{Style.RESET_ALL}")
    return error(message=f"{person_type[0:-1].title()} with ID Num: '{person_data['id_num']}' '{person_fullname}' already exists in '{school}', registration failed.", code=403)


def person_info_incomplete(person_type, required_person_data_list, person_data):
    print(f"{Fore.RED}{person_type[0:-1].title()} information incomplete")
    print("required data:")
    pprint(required_person_data_list)
    print("received data:")
    pprint(f"{person_data}{Style.RESET_ALL}")
    return {
        "success": False,
        "message": f"{person_type[0:-1].title()} information incomplete.",
        "required data": required_person_data_list,
        "received data": person_data
    }, 422


def person_not_found_in_school(school, person_type, id_num):
    print(f"{Fore.RED}{person_type[0:-1].title()} with ID Num: '{id_num}' was not found in '{school}'{Style.RESET_ALL}")
    return error(message=f"{person_type[0:-1].title()} with ID Num: '{id_num}' was not found in '{school}'", code=404)
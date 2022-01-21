import os
import json
import ujson
from datetime import datetime
from student_data_list import *
from dic import *
from errors import *
from successes import *
import qrcode
import qrcode.image.svg
from pprint import pprint
from flask import Flask, request, send_file, render_template, session, redirect, url_for, flash, send_from_directory
import firebase_admin
from firebase_admin import credentials, db


# Fetch the service account key JSON file contents or OS environ variable
try:
    cred = credentials.Certificate('private/aass-temp-database-firebase-adminsdk-uwjsh-893b46b46b.json')
    print("Successfully loaded credentials from JSON file.")
except:
    cred = credentials.Certificate({
        "project_id": os.environ.get('project_id'),
        "private_key": os.environ.get('private_key'),
        "client_email": os.environ.get('client_email'),
        "token_uri": os.environ.get('token_uri')
    })
    print("Successfully loaded credentials from environment variables.")

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://aass-temp-database-default-rtdb.asia-southeast1.firebasedatabase.app/'
})


app = Flask(__name__)

def api_not_found(e):
    return error("The requested resource was not found", 404)


def find_person_in_database(school_to_find, person_type_to_find, id_num_to_find):
    people_ref = db.reference(f"/schools/{school_to_find}/{person_type_to_find}")
    people = people_ref.get()

    if people is None:
        return False

    for id_num in people:
        if id_num == id_num_to_find:
            return {id_num: people[id_num]}

    return False


def find_school_in_database(school_to_find):
    schools_ref = db.reference(f"/schools/")
    schools = schools_ref.get()

    for school in schools:
        if school == school_to_find:
            return {school: schools[school]}

    return False


def add_school_to_database(school_to_add):
    schools_ref = db.reference(f"/schools/")
    schools_ref.update({
        school_to_add: school_to_add
    })
    return


def add_person_to_database(school, person_type, id_num, person_data):
    person_ref = db.reference(f"/schools/{school}/{person_type}/")
    person_ref.update({
        id_num: person_data
    })

    return

    
def verify_person():
    school_to_verify = request.args.get('school')
    person_type_to_verify = request.args.get('person_type')
    id_num_to_verify = request.args.get('id_num')
    print(f"Verifying if {person_type_to_verify[0:-1].title()} with ID Num: '{id_num_to_verify}' exists in '{school_to_verify}'")

    person_data = find_person_in_database(school_to_verify, person_type_to_verify, id_num_to_verify)
    if person_data != False:
        return person_found_in_school(school_to_verify, person_type_to_verify, id_num_to_verify, person_data)

    return person_not_found_in_school(school_to_verify, person_type_to_verify, id_num_to_verify)


def verify_school():
    school_to_verify = request.args.get('school')
    school_data = find_school_in_database(school_to_verify)
    print(f"Verifying if '{school_to_verify}' exists")

    if school_data != False:
        return found_school(school_to_verify, school_to_verify)

    return school_not_found(school_to_verify)


def register_school_to_firebase():
    school_to_add = request.args.get('school')
    print(find_school_in_database(school_to_add))
 
    if find_school_in_database(school_to_add):
        return school_already_exists(school_to_add)
    else:
        add_school_to_database(school_to_add)
        return added_school(school_to_add)


def verify_complete_data(required_person_data_list, person_data):
    print("Compares provided data:")
    pprint(person_data)
    print("With the required data:")
    pprint(required_person_data_list)

    # verifies if items in required info list is present in the person's data list.
    incomplete_person_data_list = []
    for info in required_person_data_list:
        if info not in person_data:
            incomplete_person_data_list.append(info)

    if len(incomplete_person_data_list) > 0:
        print("False - Incomplete data")
        return False
    else:
        print("True - Complete data")
        return True


def get_person_data(person_data_list):
    # gets all the information (based on a list) from link arguments
    person_data = {}
    for info in person_data_list:
        person_data[info] = request.args.get(info)

    return person_data


def register_person_to_firebase():
    school = request.args.get('school')
    person_type = request.args.get('person_type')
    id_num = request.args.get('id_num')
    person_data = {}

    if person_type == 'students':
        person_data_list = student_data_list
        required_person_data_list = required_student_data_list
    elif person_type == 'professors':
        return error(message="Professors aren't still supported!", code=404)
    else:
        return error(message="Invalid person_type", code=404)

    person_data = get_person_data(person_data_list)
    print(f"person_data: {person_data}")

    if verify_complete_data(required_person_data_list=required_person_data_list, person_data=person_data) == False:
        return person_info_incomplete(person_type, required_person_data_list, person_data)

    person_data = remove_empty_keys(person_data)
    print(f"person_data:")
    pprint(person_data)
    person_fullname = f"{person_data['f_nm']} {person_data.get('m_nm', ' ')} {person_data['l_nm']}"

    if find_person_in_database(school, person_type, id_num) == False:
        add_person_to_database(school, person_type, id_num, person_data)
        return person_added_to_school(school, person_type, person_data, person_fullname)
        
    else:
        return person_already_exists_in_school(school, person_type, person_data, person_fullname)


def generate_qrcode_img(data, filename_description, image_format="png"):
    if image_format == 'svg':
        img = qrcode.make(data, image_factory=qrcode.image.svg.SvgPathImage)
    else:
        img = qrcode.make(data)

    qrcode_img_path = os.path.join(f"static/qrcodes/{filename_description}.{image_format}")
    img.save(qrcode_img_path)
    
    return qrcode_img_path


def generate_qrcode_data():
    id_num = request.args.get('id_num')
    school = request.args.get('school')
    person_type = request.args.get('person_type')
    image_format = request.args.get('image_format', 'png')

    if person_type == None:
        print("person_type = ")
        return error(message="person_type None", code=404)
    elif person_type == 'students':
        print("person_type: students")
        required_person_data_list = ['id_num', 'school']
    elif person_type == 'professors':
        print("person_type: professors aren't still supported")
        return error(message="Professors aren't still supported!", code=404)
    else:
        print("invalid person_type")
        return error(message="Invalid person_type", code=404)

    person_data = request.args
    if verify_complete_data(required_person_data_list, person_data) == False:
        return person_info_incomplete(person_type, required_person_data_list, person_data)

    if find_school_in_database(school) == False:
        return school_not_found(school)

    person_data = find_person_in_database(school, person_type, id_num)
    print("person_data:")
    pprint(person_data)

    if person_data == False:
        return person_not_found_in_school(school, person_type, id_num)
    else:
        print(f"Successfully generated QR Code for {person_type[0:-1].title()} '{id_num}' of '{school}' ")
        return send_file(generate_qrcode_img(data=person_data[id_num], filename_description=f"{person_type[0:-1].title()}_{id_num}_{school}", image_format=image_format))

    
def update_person():
    pass


def update_school():
    pass


def remove_empty_keys(dictionary):
    empty_keys = []
    for key in dictionary:
        if not dictionary[key]:
            empty_keys.append(key)
    for key in empty_keys:
        print(f"Key: '{key}' empty, removing..")
        dictionary.pop(key)

    return dictionary


def minify_json(json_data):
    minified_json = ujson.dumps(json_data)
    return minified_json


@app.errorhandler(404)
def api_not_found(error):
    return "API Request invalid.", 404


@app.route('/')
def main():
    return success(message="Welcome to AASS-DIC Backend!", code=200)


@app.route('/documentation/')
def documentation_home():
    return redirect("https://blog-aass-dic-backend.lonewanderer27.repl.co/")


@app.route('/DIC/logout/')
def dic_school_logout():
    session['school_name'] = None
    return redirect('/DIC/login/')


@app.route('/DIC/generate_id/', methods=['GET', 'POST'])
def dic_gen_id():
    if request.method == 'GET':
        school_name = session.get('school_name', '')
        if find_school_in_database(school_name):
            return render_template(
                'dic_generate_id.html', 
                background=f"static/backgrounds/{school_name}/{school_name}.png",
                school_name=school_name)
        else:
            return redirect('/DIC/login')

    elif request.method == 'POST':
        person_type = request.form.get('person_type')
        id_num = request.form.get('id_num')
        school_name = request.form.get('school_name')
        print(f"person_type: {person_type}")

        if not find_school_in_database(school_name):
            return redirect('/DIC/login')

        if person_type == 'students':
            print("students triggered")
            course = request.form.get('course', )
            print(f"course: {course}")
            
            if find_person_in_database(school_name, person_type, id_num):
                pass
                if dic_verify_student_course_in_database(id_num, school_name, course):
                    print(f"{person_type[0:-1].title()} {id_num} with Course {course} found!")
                    return render_template('dic_generate_id.html', 
                    success=f"{person_type[0:-1].title()} {id_num} with Course {course} found!",
                    background=f"static/backgrounds/{school_name}/{school_name}.png",
                    school_name=school_name, id_num=id_num)

                else:
                    print(f"{person_type[0:-1].title()} {id_num} with Course {course} not found!")
                    return render_template('dic_generate_id.html', 
                    error=f"{course} for {id_num} not found!",
                    background=f"static/backgrounds/{school_name}/{school_name}.png",
                    school_name=school_name, id_num=id_num)
            else:
                return render_template('dic_generate_id.html', 
                error=f"{person_type[0:-1].title()} not found!",
                background=f"static/backgrounds/{school_name}/{school_name}.png",
                school_name=school_name, id_num=id_num)
        
        elif person_type == 'professors':
            return render_template('dic_generate_id.html', error="Professors aren't still supported")


@app.route('/DIC/login/', methods=['GET', 'POST'])
def dic_school_login():
    if request.method == 'GET':
        school_name = session.get('school_name')
        if not school_name:
            return render_template('dic_school_login.html')

        elif find_school_in_database(school_name=school_name):

            return redirect('/DIC/generate_id/')
        
    elif request.method == 'POST':
        
        school_name = request.form.get('school_name')
        print(f"school_name: {school_name}")
        if find_school_in_database(school_name):
            session['school_name'] = school_name
            return redirect('/DIC/generate_id/')
        else:
            return render_template('dic_school_login.html', 
            error="School does not exist...",
            school_name=school_name
            )


@app.route('/api/')
def determine_api_request_type():
    if len(request.args) == 0:
        return error(message="You have not provided any data!", code=404)

    print("request arguments:")
    pprint(request.args)

    request_type = request.args.get('request_type')

    if request_type == 'register_person':

        print(f"{request_type} triggered")
        return register_person_to_firebase()

    elif request_type == 'register_school':
        
        print(f"{request_type} triggered")
        return register_school_to_firebase()

    elif request_type == 'verify_school':

        print(f"{request_type} triggered")
        return verify_school()

    elif request_type == 'verify_person':

        print(f"{request_type} triggered")
        return verify_person()

    elif request_type == 'update_person':

        print(f"{request_type} triggered")
        return update_person()

    elif request_type == 'update_school':

        print(f"{request_type} triggered")
        return update_school()

    elif request_type == 'gen_qrcode':

        print(f"{request_type} triggered")
        return generate_qrcode_data()

    else:

        print("request_type did not triggered anything!")
        return api_not_found("request_type invalid!")


app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    # Binds to defined $PORT, otherwise default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
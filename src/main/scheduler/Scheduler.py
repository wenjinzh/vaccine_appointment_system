from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    """
    TODO: Part 1
    """
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("patient's Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    patient = Patient(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create patient user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create patient user.")
        print(e)
        return
    print("Created patient user ", username)

def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)# ???meaning of as_dict
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        # ??? not before the first record
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit() # ??? quit
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking patient's username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking patient's username")
        print("Error:", e)
    finally: # what if without this
        cm.close_connection()
    return False

def login_patient(tokens):
    """
    TODO: Part 1
    """
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None:
        print("User already logged in as a caregiver.")
        return
    
    if current_patient is not None:
        print("User already logged in as a patient.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver

def check_date_format(test_str):
    '''
    To check that the input date is of the correct form
    '''
    # initializing format
    format = "%m-%d-%Y"
 
    # checking if format matches the date
    res = True
 
    # using try-except to check for truth value
    try:
        res = bool(datetime.datetime.strptime(test_str, format))
    except ValueError:
        res = False
    return res


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    
    if len(tokens) != 2:
        print("Please try again!")
        return

    if check_date_format(tokens[1]) is not True:
        print("Please make sure your input date format is mm-dd-yyyy")
        return
    
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_available_caregiver = "SELECT Username FROM Availabilities WHERE Time = %s order by Username" 
    select_vaccine="select * from vaccines"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_available_caregiver, tokens[1])
        check=cursor.fetchall()
        # if there is no result from the select
        if check==[]:
            print("There is no caregiver available on ", tokens[1])
            return
        cursor.execute(select_vaccine)
        available_vaccine = cursor.fetchall()
        print("Availabe caregivers on ", tokens[1], ", available vaccines and doses remained are:\n")
        for row in check:
            for row1 in available_vaccine:
                print(row["Username"], row1["Name"], " ", row1["Doses"])
    except pymssql.Error as e:
        print("Error from pymssql occurred when searching caregiver schedule")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when searching caregiver schedule")
        print("Error:", e)
    finally: # what if without this
        cm.close_connection()
    return


def reserve(tokens):
    """
    TODO: Part 2
    """
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    if current_patient is None:
        print("Please login as a patient!")
        return
    
    if len(tokens) != 3:
        print("Please try again!")
        return

    if check_date_format(tokens[1]) is not True:
        print("Please make sure your input date format is mm-dd-yyyy")
        return
    # see vaccines available
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_vaccine_dose = "SELECT Doses FROM Vaccines WHERE Name = %s "
    cursor=conn.cursor(as_dict=True)
    cursor.execute(select_vaccine_dose, tokens[2])
    vaccine_dose_remain=cursor.fetchone()
    if not vaccine_dose_remain["Doses"]>0:
        print("Not enough available doses of", tokens[2],"!")
        return
    #print(vaccine_dose_remain)
    #print(vaccine_dose_remain["Doses"])

    # see caregivers available on that day
    select_available_cg = "SELECT * FROM Availabilities WHERE Time = %s order by Username"
    cursor.execute(select_available_cg, tokens[1])
    available_cg=cursor.fetchone()
    #print(available_cg)
    if available_cg is None:
        print("No caregiver available on ", tokens[1])
        return
    # achieving here we can have that we can make the reservation
    # change in vaccines table
    changetable_vac="UPDATE Vaccines SET Doses=%d where Name=%s"
    try:
        #print(vaccine_dose_remain["Doses"]-1, tokens[2])
        cursor.execute(changetable_vac, (vaccine_dose_remain["Doses"]-1, tokens[2]))
        conn.commit()
    except pymssql.Error as e:
        print("please try again!3")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("please try again!4")
        print("Error:", e)
        return

    # change in availabilities table
    changetable_ava="delete from Availabilities WHERE Time=%s and Username=%s"
    try:
        #print(tokens[1], available_cg["Username"])
        cursor.execute(changetable_ava, (tokens[1], available_cg["Username"]))
        conn.commit()
    except pymssql.Error as e:
        print("please try again!5")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("please try again!6")
        print("Error:", e)
        return

    # change in appointments table
    changetable_app="INSERT INTO Appointments (Time, cname, vname, pname) VALUES (%s, %s, %s, %s)"
    try:
        #print(tokens[1], available_cg["Username"], tokens[2], current_patient.get_username())
        cursor.execute(changetable_app, (tokens[1], available_cg["Username"], tokens[2], current_patient.get_username()))
        conn.commit()
    except pymssql.Error as e:
        print("please try again!1")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("please try again!2")
        print("Error:", e)
        return
    #print appointment 
    select_app="SELECT TOP 1 * from Appointments ORDER BY Appointment_id DESC"
    try:
        cursor.execute(select_app)
        print_app=cursor.fetchone()
        print("Appointment ID:%d, Caregiver username: %s" % (print_app["Appointment_id"], print_app["cname"]))
    except Exception as e:
        print("please try again!7")
        print("Error:", e)
        return
        




def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    # check 3: the input of date is the form that we want
    if check_date_format(tokens[1]) is not True:
        print("Please make sure your input date format is mm-dd-yyyy")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    pass


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    '''
    TODO: Part 2
    '''
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    if len(tokens) != 1:
        print("Please try again!")
        return

    current_user= None

    cm = ConnectionManager()
    conn = cm.create_connection()

    select_app_cg = "SELECT * FROM Appointments WHERE cname = %s order by Appointment_id" 
    select_app_p="select * FROM Appointments WHERE pname = %s order by Appointment_id"
    try:
        cursor = conn.cursor(as_dict=True)
        if current_caregiver is None:
            #current_user is a patient
            current_user=current_patient
            cursor.execute(select_app_p, current_user.get_username())
            check=cursor.fetchall()
            if check==[]:
                print("You have no appointment for now!")
                return
            print("Your current appointments:")
            for row in check:
                print(row["Appointment_id"], row["vname"], row["Time"], row["cname"])
        else:
            #current_user is a caregiver
            current_user=current_caregiver
            cursor.execute(select_app_cg, current_user.get_username())
            check=cursor.fetchall()
            if check==[]:
                print("You have no appointment for now!")
                return
            print("Your current appointments:")
            for row in check:
                print(row["Appointment_id"], row["vname"], row["Time"], row["pname"])
    except pymssql.Error as e:
        print("Please try again!1")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!2")
        print("Error:", e)
    finally: # what if without this
        cm.close_connection()
    return



def logout(tokens):
    """
    TODO: Part 2
    """
    
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    
    if current_caregiver is not None:
        current_caregiver=None
        print("Successfully logged out from a caregiver account!")
        return

    if current_patient is not None:
        current_patient=None
        print("Successfully logged out from a patient account!")
        return


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")# cannot work, always invalid operation name
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()

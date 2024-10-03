import psycopg2
from prettytable import PrettyTable

# Database connection details
conn = psycopg2.connect(
    database="postgres", user='postgres',
    password='Abed12345', host='127.0.0.1', port='5432'
)

# Function to display table in a nice tabular format
def display_table(table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    table = PrettyTable(columns)
    for row in rows:
        table.add_row(row)

    print(table)

# Function to display information about a doctor
def doctor_info(did):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctor WHERE did = %s", (did,))
    doctor = cursor.fetchone()
    if doctor:
        print("Doctor name is:", doctor[1])
        
        # Number of patients
        cursor.execute("SELECT COUNT(*) FROM patient WHERE prim_did = %s", (did,))
        num_patients = cursor.fetchone()[0]
        print("Number of patients Doctor has as a primary:", num_patients)
        
        # Names of patients
        cursor.execute("SELECT pid, pname FROM patient WHERE prim_did = %s", (did,))
        patients = cursor.fetchall()
        print("\nHis/her patients names:")
        for idx, patient in enumerate(patients, start=1):
            print(f"{idx} : {patient[1]}")
        
        # Pharmacies supervised
        cursor.execute("SELECT hid, pharm_name FROM pharmacy WHERE supervis_id = %s", (did,))
        pharmacies = cursor.fetchall()
        if pharmacies:
            print("\nThe pharmacies this doctor supervises:")
            for idx, pharmacy in enumerate(pharmacies, start=1):
                print(f"{idx} : {pharmacy[1]}")
        else:
            print("\nNo pharmacies supervised")
        
        # Prescribed drugs
        cursor.execute("SELECT drug_id, drug_name, formula FROM drug JOIN prescribes ON drug.mid = prescribes.drug_id WHERE prescribes.doctor_id = %s", (did,))
        drugs = cursor.fetchall()
        if drugs:
            print("\nThe drugs and their respective formulas this doctor prescribes:")
            for idx, drug in enumerate(drugs, start=1):
                print(f"{idx} : {drug[1]} {drug[2]}")
        else:
            print("\nNo prescribed drugs")
    else:
        print("Doctor ID not found")


# Function to display information about a patient
def patient_info(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patient WHERE pid = %s", (pid,))
    patient = cursor.fetchone()
    if patient:
        print("Patient name is:", patient[1])
        
        # Primary doctor
        cursor.execute("SELECT dname FROM doctor WHERE did = %s", (patient[4],))
        doctor_name = cursor.fetchone()[0]
        print("Primary Doctor is:", doctor_name)
        
        # Prescribed drugs
        cursor.execute("SELECT drug.drug_name, drug.formula FROM drug JOIN prescribes ON drug.mid = prescribes.drug_id WHERE prescribes.patient_id = %s", (pid,))
        drugs = cursor.fetchall()
        if drugs:
            print("\nThe drugs and respective formulas prescribed are:")
            for idx, drug in enumerate(drugs, start=1):
                print(f"{idx} : {drug[0]} {drug[1]}")
        else:
            print("\nNo Prescribed Drugs")
    else:
        print("Patient ID not found")

# Function to insert a new patient
def insert_patient():
    pid = int(input("Enter Patient ID: "))
    pname = input("Enter Patient name: ")
    while not pname:
        print("Error: Patient name cannot be empty.")
        pname = input("Enter Patient name: ")
    paddress = input("Enter Patient address (optional): ").strip() or None
    page_input = input("Enter Patient age (optional): ").strip()
    page = int(page_input) if page_input else None

    try:
        # Retrieve doctor IDs and names
        cursor = conn.cursor()
        cursor.execute("SELECT did, dname FROM doctor")
        doctors = cursor.fetchall()
        
        # Display available doctors after patient added
        print("\nThe available doctors are:")
        for idx, doctor in enumerate(doctors, start=1):
            print(f"{idx} : {doctor[0]} {doctor[1]}")
        
        prim_did = int(input("\nEnter primary doctor ID from these: "))
        while prim_did not in [doctor[0] for doctor in doctors]:
            prim_did = int(input("Invalid doctor ID. Enter primary doctor ID from the provided list: "))
    
        cursor.execute("INSERT INTO patient (pid, pname, paddress, age, prim_did) VALUES (%s, %s, %s, %s, %s)", (pid, pname, paddress, page, prim_did))
        conn.commit()
        print("Patient Successfully Added")
        print("Primary Doctor Successfully Assigned")
    except psycopg2.IntegrityError as e:
        conn.rollback()
        print("Error:", e)
        print("Failed to insert patient. Patient ID already exists.")
    except psycopg2.Error as e:
        conn.rollback()
        print("Error:", e)
        print("Failed to insert patient.")


# Main menu loop
while True:
    print("\nEnter D to print all the doctors")
    print("Enter P to print all the patients")
    print("Enter d to print all the information about a doctor")
    print("Enter p to print all the information about a patient")
    print("Enter i to insert a new patient")
    print("Enter q to quit")

    choice = input("Choice: ")

    if choice == 'D':
        display_table("doctor")
    elif choice == 'P':
        display_table("patient")
    elif choice == 'd':
        did = int(input("Enter Doctor ID: "))
        doctor_info(did)
    elif choice == 'p':
        pid = int(input("Enter Patient ID: "))
        patient_info(pid)
    elif choice == 'i':
        insert_patient()
    elif choice == 'q':
        break
    else:
        print("Invalid choice")

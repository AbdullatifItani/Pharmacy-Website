from flask import Flask, request
from flask import render_template
import psycopg2

app = Flask(__name__)

# Database connection details
conn = psycopg2.connect(
    database="postgres", user='postgres',
    password='Abed12345', host='127.0.0.1', port='5432'
)

# Function to fetch data from the database
def fetch_data(query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# index
@app.route('/')
def index():
    return render_template('home.html')

# Part A
@app.route('/display_tables_and_doctor_information', methods=['GET', 'POST'])
def display_tables_and_doctor_information():
    if request.method == 'POST':
        doctors = fetch_data("SELECT * FROM doctor")
        
        patients = fetch_data("SELECT * FROM patient")
        
        drugs = fetch_data("SELECT * FROM drug")
        
        pharmacies = fetch_data("SELECT * FROM pharmacy")
        
        # Handle form submission
        docid = request.form['docid']
        doctor_data = fetch_data(f"SELECT * FROM doctor WHERE did = {docid}")
        if doctor_data:
            # Example: Fetch number of patients for the doctor
            num_patients = fetch_data(f"SELECT COUNT(*) FROM patient WHERE prim_did = {docid}")[0][0]
        
            # Example: Fetch names of patients
            patient_names = fetch_data(f"SELECT pname FROM patient WHERE prim_did = {docid}")
        
            # Example: Fetch pharmacies supervised by the doctor
            pharmacies_supervised = fetch_data(f"SELECT pharm_name FROM pharmacy WHERE supervis_id = {docid}")
        
            # Example: Fetch prescribed drugs for all patients of the doctor
            prescribed_drugs = fetch_data(f"SELECT drug_name FROM drug JOIN prescribes ON drug.mid = prescribes.drug_id WHERE prescribes.doctor_id = {docid}")
            
            num_patients_all = fetch_data(f"SELECT COUNT(*) FROM patient")[0][0]
            
            return render_template('index4T.html', cc="Doctor Information", rows1=doctors, rows2=patients, rows3=drugs, rows4=pharmacies, doct=doctor_data[0][1], numall=num_patients_all, num=num_patients, pat=[patient[0] for patient in patient_names], drugsall=[drug[0] for drug in prescribed_drugs], pharm=[pharmacies_supervised[0] for pharmacy in pharmacies_supervised])
        else:
            error_msg = f"Doctor with ID {docid} not found."
            return render_template('index4T.html', cc=error_msg, rows1=doctors, rows2=patients, rows3=drugs, rows4=pharmacies)
    else:
        # Handle GET request
        doctors = fetch_data("SELECT * FROM doctor")
        
        patients = fetch_data("SELECT * FROM patient")
        
        drugs = fetch_data("SELECT * FROM drug")
        
        pharmacies = fetch_data("SELECT * FROM pharmacy")
        
        return render_template('index4T.html', cc="Database Content", rows1=doctors, rows2=patients, rows3=drugs, rows4=pharmacies)

    

# Part B
@app.route('/insert_patient', methods=['GET', 'POST'])
def insert_patient():
    if request.method == 'POST':
        # Get form data
        pid = request.form['pid']
        pname = request.form['pname']
        paddress = request.form['paddress']
        page = request.form['page']
        prim_did = request.form['prim_did']
        
        try:
            # Insert new patient into the database
            cursor = conn.cursor()
            cursor.execute("INSERT INTO patient (pid, pname, paddress, age, prim_did) VALUES (%s, %s, %s, %s, %s)", (pid, pname, paddress, page, prim_did))
            conn.commit()
            
            # Redirect to a success page or display a success message
            return render_template('success.html', message="Patient successfully added.")
        except psycopg2.Error as e:
            # Handle and print database error
            print(e)
            conn.rollback()
            error_message = "Failed to insert patient. Please try again."
            return render_template('error.html', error=error_message)
    else:
        # Render the HTML form for adding a new patient
        return render_template('insert_patient.html')
    

# Part C
@app.route('/insert_doctor', methods=['GET', 'POST'])
def insert_doctor():
    if request.method == 'POST':
        # Get form data
        did = request.form['did']
        dname = request.form['dname']
        specialty = request.form['specialty']
        years_of_exp = request.form['years_of_exp']
        patient_id = request.form['patient_id']
        is_primary = request.form.get('is_primary')  # Check if the doctor is primary
        
        try:
            # Insert new doctor into the database
            cursor = conn.cursor()
            cursor.execute("INSERT INTO doctor (did, dname, specialty, years_of_exp) VALUES (%s, %s, %s, %s)", (did, dname, specialty, years_of_exp))
            
            # If the doctor is primary, update the patient's primary doctor ID
            if is_primary:
                cursor.execute("SELECT pid FROM patient WHERE pid = %s", (patient_id,))
                patient_exists = cursor.fetchone() is not None
        
                if patient_exists:
                    cursor.execute("UPDATE patient SET prim_did = %s WHERE pid = %s", (did, patient_id))
                else:
                    raise psycopg2.Error("Patient with ID {} does not exist.".format(patient_id))
            
            conn.commit()
            
            # Redirect to a success page or display a success message
            return render_template('success.html', message="Doctor successfully added.")
        except psycopg2.Error as e:
            # Handle and print database error
            print(e)
            conn.rollback()
            error_message = "Failed to insert doctor. Please try again."
            return render_template('error.html', error=error_message)
    else:
        # Render the HTML form for adding a new doctor
        return render_template('insert_doctor.html')


# Part D
@app.route('/insert_pharmacy', methods=['GET', 'POST'])
def insert_pharmacy():
    if request.method == 'POST':
        # Get form data
        hid = request.form['hid']
        pharm_name = request.form['pharm_name']
        pharm_location = request.form['pharm_location']
        supervis_id = request.form['supervis_id']
        
        try:
            # Insert new pharmacy into the database
            cursor = conn.cursor()
            cursor.execute("INSERT INTO pharmacy (hid, pharm_name, pharm_location, supervis_id) VALUES (%s, %s, %s, %s)", (hid, pharm_name, pharm_location, supervis_id))
            conn.commit()
            
            # Redirect to a success page or display a success message
            return render_template('success.html', message="Pharmacy successfully added.")
        except psycopg2.Error as e:
            # Handle and print database error
            print(e)
            conn.rollback()
            error_message = "Failed to insert pharmacy. Please try again."
            return render_template('error.html', error=error_message)
    else:
        # Render the HTML form for adding a new pharmacy
        return render_template('insert_pharmacy.html')


# Part E
@app.route('/insert_prescription', methods=['GET', 'POST'])
def insert_prescription():
    if request.method == 'POST':
        # Get form data
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        drug_id = request.form['drug_id']
        p_date = request.form['p_date']
        prescription = request.form['prescription']

        try:
            # Insert new prescription into the database
            cursor = conn.cursor()
            cursor.execute("INSERT INTO prescribes (patient_id, doctor_id, drug_id, p_date, prescription) VALUES (%s, %s, %s, %s, %s)", (patient_id, doctor_id, drug_id, p_date, prescription))
            conn.commit()

            # Return success message
            return render_template('success.html', message="Prescription successfully added.")
        except psycopg2.Error as e:
            # Handle and print database error
            print(e)
            conn.rollback()
            error_message = "Failed to insert prescription. Please try again."
            return render_template('error.html', error=error_message)
    else:
        # Render the HTML form for adding a new pharmacy
        return render_template('insert_prescription.html')
    
    
# Part F
@app.route('/patients_and_pharmacies', methods=['GET', 'POST'])
def patients_and_pharmacies():
    if request.method == 'POST':
        # Get location input from the form
        location = request.form['location']
        
        # Fetch patients living in the specified location
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patient WHERE paddress LIKE %s", (location,))
        patients = cursor.fetchall()

        # Fetch pharmacies located in the specified location
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pharmacy WHERE pharm_location LIKE %s", (location,))
        pharmacies = cursor.fetchall()
        
        return render_template('patients_and_pharmacies.html', patients=patients, pharmacies=pharmacies, location=location)
    else:
        return render_template('location_input.html')
    

# Part G
@app.route('/drug_prescriptions')
def drug_prescriptions():
    # Fetch all rows from the result
    drug_prescription_counts = fetch_data("SELECT drug.drug_name, COUNT(DISTINCT prescribes.doctor_id) AS num_doctors FROM drug LEFT JOIN prescribes ON drug.mid = prescribes.drug_id GROUP BY drug.drug_name")
    
    # Render the template with drug prescription information
    return render_template('drug_prescriptions.html', drug_prescription_counts=drug_prescription_counts)


# Part H
@app.route('/patient_info', methods=['GET', 'POST'])
def patient_info():
    if request.method == 'POST':
        # Get patient name input from the form
        patient_name = request.form['patient_name']
        
        # Fetch patient information
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patient WHERE pname = %s", (patient_name,))
        patient_info = cursor.fetchone()
        
        if patient_info:
            # Get patient ID
            patient_id = patient_info[0]
            
            # Get primary doctor ID
            primary_doctor_id = patient_info[4]
            
            # Fetch primary doctor information
            cursor.execute("SELECT * FROM doctor WHERE did = %s", (primary_doctor_id,))
            primary_doctor_info = cursor.fetchone()
            
            # Fetch other doctors' information
            cursor.execute("SELECT doctor.* FROM doctor JOIN examines ON doctor.did = examines.doctor_id WHERE examines.patient_id = %s AND doctor.did != %s", (patient_id, primary_doctor_id,))
            other_doctor_info = cursor.fetchall()

            # Fetch drugs taken by the patient
            cursor.execute("SELECT drug_name FROM drug JOIN prescribes ON drug.mid = prescribes.drug_id WHERE prescribes.patient_id = %s", (patient_id,))
            drugs_taken = [row[0] for row in cursor.fetchall()]
            
            # Render the template with patient information
            return render_template('patient_info.html', patient_id=patient_id, patient_name=patient_name, primary_doctor_info=primary_doctor_info, other_doctor_info=other_doctor_info, drugs_taken=drugs_taken)
        else:
            # Patient not found
            error_message = f"No patient found with the name '{patient_name}'."
            return render_template('error.html', error=error_message)
    else:
        return render_template('patient_input.html')


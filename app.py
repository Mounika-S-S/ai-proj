from flask import Flask, render_template, request
from db_config import SessionLocal
from models import Project, Team, Working, Employee, Student, Person
from ai_utils import generate_personal_statement, generate_team_members
from datetime import date

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


# ✅ Personal Statement
@app.route('/personal_statement', methods=['GET', 'POST'])
def personal_statement():
    statement = ""
    message = ""
    if request.method == 'POST':
        person_id = request.form.get('person_id', '').strip()
        person_name = request.form.get('person_name', '').strip()

        session = SessionLocal()

        person = None
        person_obj = None
        # Try to find person by ID in Employee or Student
        if person_id:
            person = session.query(Employee).filter(Employee.employee_id == int(person_id)).first()
            if not person:
                person = session.query(Student).filter(Student.id == int(person_id)).first()
        # If not found by ID, try by name
        if not person and person_name:
            person = session.query(Employee).filter(Employee.empname.ilike(f"%{person_name}%")).first()
            if not person:
                person = session.query(Student).filter(Student.name.ilike(f"%{person_name}%")).first()

        if not person:
            message = "Person not found with given ID or name."
        else:
            # Gather projects worked on by this person (if employee)
            projects = []
            if isinstance(person, Employee):
                working_entries = session.query(Working).filter(Working.employee_id == person.employee_id).all()
                for w in working_entries:
                    proj = session.query(Project).filter(Project.id == w.projectid).first()
                    if proj:
                        projects.append(proj.name)
                # Fetch related Person object for Employee
                person_obj = session.query(Person).filter(Person.id == person.person_id).first()
            elif isinstance(person, Student):
                person_obj = session.query(Person).filter(Person.id == person.personid).first()

            # Prepare all attributes from Person
            person_attrs = {}
            if person_obj:
                person_attrs = {column.name: getattr(person_obj, column.name) for column in person_obj.__table__.columns}
            # Prepare all attributes from Employee or Student
            person_type_attrs = {}
            if isinstance(person, Employee):
                person_type_attrs = {column.name: getattr(person, column.name) for column in person.__table__.columns}
            elif isinstance(person, Student):
                person_type_attrs = {column.name: getattr(person, column.name) for column in person.__table__.columns}

            # Format statement as key: value lines for all attributes
            statement_lines = []
            statement_lines.append("Person Table Attributes:")
            for key, value in person_attrs.items():
                statement_lines.append(f"{key}: {value}")
            statement_lines.append("")
            if isinstance(person, Employee):
                statement_lines.append("Employee Table Attributes:")
            elif isinstance(person, Student):
                statement_lines.append("Student Table Attributes:")
            for key, value in person_type_attrs.items():
                statement_lines.append(f"{key}: {value}")

            if projects:
                statement_lines.append("")
                statement_lines.append(f"Projects: {', '.join(projects)}")

            statement = "\n".join(str(line) for line in statement_lines)

    ai_statement = ""
    if statement:
        # Construct prompt for AI from the statement details
        prompt = f"Please write a concise, impressive, and unique personal statement based on the following details:\n{statement}"
        ai_statement = generate_personal_statement(prompt)

    return render_template('personal_statement.html', statement=statement, ai_statement=ai_statement, message=message)

# ✅ Generate Team & Create Project
@app.route('/generate_team', methods=['GET', 'POST'])
def generate_team():
    result = {}
    if request.method == 'POST':
        prompt = request.form['prompt']
        session = SessionLocal()

        # ➡️ Create Project
        new_project = Project(
            compid=1,
            name=f"Generated Project {prompt[:10]}",
            description=prompt,
            startdate=date.today(),
            enddate=date(2025, 12, 31),
            status="active",
            teamid=None
        )
        session.add(new_project)
        session.commit()

        # ➡️ Generate Team
        roles = generate_team_members(prompt)

        # Create Employee entries for generated roles if not exist
        created_employees = {}
        for member in roles:
            existing_emp = session.query(Employee).filter(Employee.empname == f"Employee {member['employee_id']}").first()
            if not existing_emp:
                # Create a Person entry for the employee with no null columns
                new_person = Person(
                    name=f"Employee {member['employee_id']}",
                    email=f"employee{member['employee_id']}@example.com",
                    phone="000-000-0000",
                    address="Unknown Address"
                )
                session.add(new_person)
                session.flush()  # to get new_person.id

                new_emp = Employee(
                    empname=f"Employee {member['employee_id']}",
                    person_id=new_person.id,
                    dept_id=1,  # default department id
                    experience=0,
                    role="Developer",  # default role
                    company="Default Company",
                    hire_date=date.today(),
                    salary=30000,
                    phone="000-000-0000",
                    projectid=new_project.id,
                    teamid=None
                )
                session.add(new_emp)
                session.flush()  # to get new_emp.employee_id
                created_employees[member['employee_id']] = new_emp.employee_id
            else:
                created_employees[member['employee_id']] = existing_emp.employee_id
        session.commit()

        # ➡️ Create Team
        lead_employee_id = created_employees.get(roles[0]['employee_id'])
        new_team = Team(
            projid=new_project.id,
            name="AI Generated Team",
            description="Auto-generated by AI",
            lead_id=lead_employee_id
        )
        session.add(new_team)
        session.commit()

        # ➡️ Update project with teamid
        new_project.teamid = new_team.teamid
        session.commit()

        # ➡️ Add members to 'working' table
        for member in roles:
            working_entry = Working(
                employee_id=created_employees.get(member['employee_id']),
                projectid=new_project.id,
                assigned_date=date.today(),
                role_in_team=member['role'],
                teamid=new_team.teamid
            )
            session.add(working_entry)
        session.commit()

        result['message'] = f"✅ Project '{new_project.name}' and Team created with {len(roles)} members."
        result['team_members'] = roles

        return render_template('generate_team.html', result=result)
    else:
        return render_template('generate_team.html', result=result)

# ✅ Connect Students/Employees
@app.route('/connect', methods=['GET', 'POST'])
def connect():
    mentor_mentee = []
    details = []
    message = ""
    if request.method == 'POST':
        connect_type = request.form['connect_type']
        user_id = request.form['user_id']
        interest = request.form.get('interest', '').strip()

        session = SessionLocal()

        if connect_type in ['student', 'fresher']:
            import random
            # Get the student/fresher by ID
            student = session.query(Student).filter(Student.id == int(user_id)).first()
            if not student:
                message = f"No {connect_type} found with ID {user_id}."
            else:
                # Fetch related Person object for mentee
                mentee_person = session.query(Person).filter(Person.id == student.personid).first()

                # If interest input is provided, override student's interest
                if interest:
                    student.interest = interest

                # Find all employees joined with Person with person_id between 1 and 10
                mentors_with_person = session.query(Employee, Person).join(Person, Employee.person_id == Person.id).filter(Person.id.between(1, 10)).all()

                if not mentors_with_person:
                    message = "No mentors found."
                else:
                    # Select one random mentor with person
                    mentor, mentor_person = random.choice(mentors_with_person)
                    print(f"DEBUG: Mentor Person Email: {mentor_person.email}")  # Debug print
                    mentor_mentee.append({'mentor': mentor, 'mentor_person': mentor_person, 'mentee': student, 'mentee_person': mentee_person})

        elif connect_type == 'employee':
            # Fetch working entries based on employee_id
            details = session.query(Working).filter(Working.employee_id == int(user_id)).all()
            if not details:
                message = f"No working details found for employee ID {user_id}."
        else:
            message = "Invalid connect type selected."

    return render_template('connect.html', mentor_mentee=mentor_mentee, details=details, message=message)


if __name__ == "__main__":
    app.run(debug=True)

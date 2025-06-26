from sqlalchemy import Column, Integer, String, Date, ForeignKey
from db_config import Base

class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    compid = Column(Integer)
    name = Column(String)
    description = Column(String)
    startdate = Column(Date)
    enddate = Column(Date)
    status = Column(String)
    teamid = Column(Integer)

class Team(Base):
    __tablename__ = 'team'

    teamid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    projid = Column(Integer, ForeignKey('project.id'))
    name = Column(String)
    description = Column(String)
    lead_id = Column(Integer)

class Working(Base):
    __tablename__ = 'working'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer)
    projectid = Column(Integer)
    assigned_date = Column(Date)
    role_in_team = Column(String)
    teamid = Column(Integer)

class Employee(Base):
    __tablename__ = 'employee'

    employee_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('person.id'))
    empname = Column(String)
    dept_id = Column(Integer, ForeignKey('department.id'))
    experience = Column(Integer)
    role = Column(String)
    company = Column(String)
    hire_date = Column(Date)
    salary = Column(Integer)
    phone = Column(String)
    projectid = Column(Integer, ForeignKey('project.id'))
    teamid = Column(Integer, ForeignKey('team.teamid'))

class Student(Base):
    __tablename__ = 'student'

    id = Column(Integer, primary_key=True, index=True)
    personid = Column(Integer)
    admission_number = Column(String)
    year = Column(Integer)
    program = Column(String)
    admission_date = Column(Date)
    dept_id = Column(Integer)
    lang = Column(String)
    interest = Column(String)

class Department(Base):
    __tablename__ = 'department'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    head_id = Column(Integer)

class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    phone = Column(String)
    email = Column(String)
    address = Column(String)
    dob = Column(Date)

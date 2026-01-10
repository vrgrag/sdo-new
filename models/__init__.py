# users / auth
from models.users import Users
from models.roles import Role
from models.positions import Position

# companies / departments
from models.companies import Company
from models.departments import Department

# courses
from models.courses import Courses
from models.courses_company import CourseCompany
from models.courses_department import CourseDepartment
from models.course_enrollments import CourseEnrollment

# materials / lessons
from models.materials import Materials
from models.lessons import Lessons


# tests
from models.tests import Tests
from models.questions import Question
from models.answers import Answer
from models.users_answers import UserAnswer

# groups
from models.groups import Groups
from models.groups_users import GroupsUsers
from models.groups_courses import GroupsCourses
from models.groups_programs import GroupProgram

# training programs
from models.programs import TrainingProgram
from models.training_programs_users import TrainingProgramsUsers
from models.training_programs_courses import TrainingProgramsCourses

# tasks
from models.tasks import Tasks

# chat
from models.chats import Chat
from models.messages import Message

# events
from models.events import Event
from models.attendances import Attendance

from models.department_positions import DepartmentPosition
from models.company_departments import CompanyDepartment

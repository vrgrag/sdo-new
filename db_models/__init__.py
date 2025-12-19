# users / auth
from db_models.users import Users
from db_models.roles import Role
from db_models.positions import Position

# companies / departments
from db_models.companies import Company
from db_models.departments import Department

# courses
from db_models.courses import Courses
from db_models.courses_company import CourseCompany
from db_models.courses_department import CourseDepartment

# materials / modules
from db_models.materials import Materials


# tests
from db_models.tests import Tests
from db_models.questions import Question
from db_models.answers import Answer
from db_models.users_answers import UserAnswer

# groups
from db_models.groups import Groups
from db_models.groups_users import GroupsUsers
from db_models.groups_courses import GroupsCourses
from db_models.groups_programs import GroupProgram

# training programs
from db_models.programs import TrainingPrograms
from db_models.training_programs_users import TrainingProgramsUsers
from db_models.training_programs_courses import TrainingProgramCourse

# tasks
from db_models.tasks import Tasks

# chat
from db_models.chats import Chat
from db_models.messages import Message

# events
from db_models.events import Event
from db_models.attendances import Attendance

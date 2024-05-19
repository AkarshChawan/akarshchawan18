from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.libs import assertions
from core.models.assignments import Assignment, AssignmentStateEnum

from .schema import AssignmentSchema, AssignmentGradeSchema
principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)


@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of submitted or graded assignments"""
    principal_assignments = Assignment.get_all_submitted_or_graded_assignments()
    principal_assignments_dump = AssignmentSchema().dump(principal_assignments, many=True)
    return APIResponse.respond(data=principal_assignments_dump)


@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def regrade_assignment(p, incoming_payload):
    """Regrades an assignment"""
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)

    assignment = Assignment.get_by_id(grade_assignment_payload.id)

    print("////////////////////first time/////////////////////")
    print(assignment.content)
    print(assignment.state)
    print(assignment.grade)
    print("////////////////////first time/////////////////////")
    print()
    print()

    assertions.assert_found(assignment, 'No assignment with this id was found')


    assertions.assert_valid(assignment.state != AssignmentStateEnum.DRAFT,
                            'Assignment in draft state can not be graded')

    # assertions.assert_valid(
    #     assignment.state == AssignmentStateEnum.GRADED or assignment.state == AssignmentStateEnum.SUBMITTED,
    #     'Assignment in draft state can not be graded')



    print("this should not be reacheddddddddddddddddddddddddddddddddddddddddddd    ************** -------------------------")

    assertions.assert_valid(p.principal_id is not None,
                            'Assignment has been submitted to another teacher')


    graded_assignment = Assignment.mark_grade(
        _id=grade_assignment_payload.id,
        grade=grade_assignment_payload.grade,
        auth_principal=p
    )
    # db.session.commit()
    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)

    print("////////////////////second time/////////////////////")
    print(assignment.content)
    print(assignment.state)
    print(assignment.grade)
    print("////////////////////second time/////////////////////")
    print()
    print()

    return APIResponse.respond(data=graded_assignment_dump)

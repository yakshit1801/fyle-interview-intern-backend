import json
import pytest
from app import app, db
# from core.models import Assignment, Teacher, Principal
from core.models.teachers import Teacher
from core.models.assignments import Assignment
from core.models.principals import Principal



@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Add sample data for testing
            teacher1 = Teacher(user_id=1)
            teacher2 = Teacher(user_id=2)
            principal = Principal(user_id=3)
            assignment1 = Assignment(content="Test Assignment 1", state="SUBMITTED", student_id=1, teacher_id=1)
            assignment2 = Assignment(content="Test Assignment 2", state="SUBMITTED", student_id=2, teacher_id=1)
            db.session.add_all([teacher1, teacher2, principal, assignment1, assignment2])
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_teacher_grade_assignment(client):
    # Teacher grading an assignment
    headers = {
        'X-Principal': json.dumps({"user_id":1, "teacher_id":1})
    }
    response = client.post('/teacher/Assignment/grade', headers=headers, json={
        "id": 1,
        "grade": "A"
    })
    assert response.status_code == 200
    data = response.get_json()['data']
    assert data['grade'] == "A"
    assert data['state'] == "GRADED"

def test_teacher_unauthorized_grading(client):
    # Unauthorized teacher trying to grade an assignment
    headers = {
        'X-Principal': json.dumps({"user_id":2, "teacher_id":2})
    }
    response = client.post('/teacher/Assignment/grade', headers=headers, json={
        "id": 1,
        "grade": "A"
    })
    assert response.status_code == 404

def test_principal_grade_assignment(client):
    # Principal grading an assignment
    headers = {
        'X-Principal': json.dumps({"user_id":3, "principal_id":1})
    }
    response = client.post('/principal/Assignment/grade', headers=headers, json={
        "id": 1,
        "grade": "B"
    })
    assert response.status_code == 200
    data = response.get_json()['data']
    assert data['grade'] == "B"
    assert data['state'] == "GRADED"

def test_grade_nonexistent_assignment(client):
    # Grading a nonexistent assignment
    headers_teacher = {
        'X-Principal': json.dumps({"user_id":1, "teacher_id":1})
    }
    response_teacher = client.post('/teacher/Assignment/grade', headers=headers_teacher, json={
        "id": 999,
        "grade": "A"
    })
    assert response_teacher.status_code == 404

    headers_principal = {
        'X-Principal': json.dumps({"user_id":3, "principal_id":1})
    }
    response_principal = client.post('/principal/Assignment/grade', headers=headers_principal, json={
        "id": 999,
        "grade": "B"
    })
    assert response_principal.status_code == 404

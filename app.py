from flask import Flask, request, jsonify
from core.models import db, assignments, teachers, principals
from core.models.db import initialize_db
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
# Assume this function is defined elsewhere to initialize the database
# with the necessary models and configurations

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)


@app.route('/student/assignments', methods=['GET'])
def get_student_assignments():
    principal_info = request.headers.get('X-principals')
    principal_info = json.loads(principal_info)

    if 'student_id' not in principal_info:
        return jsonify({"error": "Unauthorized"}), 403

    student_id = principal_info['student_id']
    assignments = assignments.query.filter_by(student_id=student_id).all()
    data = [{
        "id": assignment.id,
        "content": assignment.content,
        "created_at": assignment.created_at,
        "updated_at": assignment.updated_at,
        "state": assignment.state,
        "grade": assignment.grade,
        "student_id": assignment.student_id,
        "teacher_id": assignment.teacher_id
    } for assignment in assignments]

    return jsonify({"data": data}), 200

@app.route('/student/assignments', methods=['POST'])
def create_or_edit_assignment():
    principal_info = request.headers.get('X-principals')
    principal_info = json.loads(principal_info)

    if 'student_id' not in principal_info:
        return jsonify({"error": "Unauthorized"}), 403

    payload = request.json
    assignment_id = payload.get('id')
    content = payload.get('content')
    student_id = principal_info['student_id']

    if assignment_id:
        assignment = assignments.query.get(assignment_id)
        if not assignment or assignment.student_id != student_id:
            return jsonify({"error": "assignments not found or unauthorized"}), 404
        assignment.content = content
    else:
        assignment = assignments(content=content, student_id=student_id, state="DRAFT")
        db.session.add(assignment)

    db.session.commit()

    data = {
        "id": assignment.id,
        "content": assignment.content,
        "created_at": assignment.created_at,
        "updated_at": assignment.updated_at,
        "state": assignment.state,
        "grade": assignment.grade,
        "student_id": assignment.student_id,
        "teacher_id": assignment.teacher_id
    }

    return jsonify({"data": data}), 200

@app.route('/student/assignments/submit', methods=['POST'])
def submit_assignment():
    principal_info = request.headers.get('X-principals')
    principal_info = json.loads(principal_info)

    if 'student_id' not in principal_info:
        return jsonify({"error": "Unauthorized"}), 403

    payload = request.json
    assignment_id = payload.get('id')
    teacher_id = payload.get('teacher_id')
    student_id = principal_info['student_id']

    assignment = assignments.query.get(assignment_id)
    if not assignment or assignment.student_id != student_id or assignment.state != "DRAFT":
        return jsonify({"error": "assignments not found or unauthorized"}), 404

    assignment.teacher_id = teacher_id
    assignment.state = "SUBMITTED"
    db.session.commit()

    data = {
        "id": assignment.id,
        "content": assignment.content,
        "created_at": assignment.created_at,
        "updated_at": assignment.updated_at,
        "state": assignment.state,
        "grade": assignment.grade,
        "student_id": assignment.student_id,
        "teacher_id": assignment.teacher_id
    }

    return jsonify({"data": data}), 200

@app.route('/teacher/assignments', methods=['GET'])
def get_teacher_assignments():
    principal_info = request.headers.get('X-principals')
    principal_info = json.loads(principal_info)

    if 'teacher_id' not in principal_info:
        return jsonify({"error": "Unauthorized"}), 403

    teacher_id = principal_info['teacher_id']
    assignments = assignments.query.filter_by(teacher_id=teacher_id, state="SUBMITTED").all()
    data = [{
        "id": assignment.id,
        "content": assignment.content,
        "created_at": assignment.created_at,
        "updated_at": assignment.updated_at,
        "state": assignment.state,
        "grade": assignment.grade,
        "student_id": assignment.student_id,
        "teacher_id": assignment.teacher_id
    } for assignment in assignments]

    return jsonify({"data": data}), 200

@app.route('/teacher/assignments/grade', methods=['POST'])
def grade_assignment():
    principal_info = request.headers.get('X-principals')
    principal_info = json.loads(principal_info)

    if 'teacher_id' not in principal_info:
        return jsonify({"error": "Unauthorized"}), 403

    payload = request.json
    assignment_id = payload.get('id')
    grade = payload.get('grade')
    teacher_id = principal_info['teacher_id']

    assignment = assignments.query.get(assignment_id)
    if not assignment or assignment.teacher_id != teacher_id or assignment.state != "SUBMITTED":
        return jsonify({"error": "assignments not found or unauthorized"}), 404

    assignment.grade = grade
    assignment.state = "GRADED"
    db.session.commit()

    data = {
        "id": assignment.id,
        "content": assignment.content,
        "created_at": assignment.created_at,
        "updated_at": assignment.updated_at,
        "state": assignment.state,
        "grade": assignment.grade,
        "student_id": assignment.student_id,
        "teacher_id": assignment.teacher_id
    }

    return jsonify({"data": data}), 200

@app.route('/principal/assignments', methods=['GET'])
def get_principal_assignments():
    principal_info = request.headers.get('X-principals')
    principal_info = json.loads(principal_info)

    if 'principal_id' not in principal_info:
        return jsonify({"error": "Unauthorized"}), 403

    assignments = assignments.query.all()
    data = [{
        "id": assignment.id,
        "content": assignment.content,
        "created_at": assignment.created_at,
        "updated_at": assignment.updated_at,
        "state": assignment.state,
        "grade": assignment.grade,
        "student_id": assignment.student_id,
        "teacher_id": assignment.teacher_id
    } for assignment in assignments]

    return jsonify({"data": data}), 200

@app.route('/principal/teachers', methods=['GET'])
def get_principal_teachers():
    principal_info = request.headers.get('X-principals')
    principal_info = json.loads(principal_info)

    if 'principal_id' not in principal_info:
        return jsonify({"error": "Unauthorized"}), 403

    teachers = teachers.query.all()
    data = [{
        "id": teacher.id,
        "user_id": teacher.user_id,
        "created_at": teacher.created_at,
        "updated_at": teacher.updated_at
    } for teacher in teachers]

    return jsonify({"data": data}), 200

@app.route('/principal/assignments/grade', methods=['POST'])
def principal_grade_assignment():
    principal_info = request.headers.get('X-principals')
    principal_info = json.loads(principal_info)

    if 'principal_id' not in principal_info:
        return jsonify({"error": "Unauthorized"}), 403

    payload = request.json
    assignment_id = payload.get('id')
    grade = payload.get('grade')

    assignment = assignments.query.get(assignment_id)
    if not assignment:
        return jsonify({"error": "assignments not found"}), 404

    assignment.grade = grade
    assignment.state = "GRADED"
    db.session.commit()

    data = {
        "id": assignment.id,
        "content": assignment.content,
        "created_at": assignment.created_at,
        "updated_at": assignment.updated_at,
        "state": assignment.state,
        "grade": assignment.grade,
        "student_id": assignment.student_id,
        "teacher_id": assignment.teacher_id
    }

    return jsonify({"data": data}), 200

if __name__ == '__main__':
    app.run(debug=True)

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.course import Course
from app.models.course_students import CourseStudents
from app.utils.response import Result
from app import db
from app.student import student_course_bp



@student_course_bp.route('/list', methods=['GET'])
@jwt_required()
def get_student_courses():
    try:
        user_id = int(get_jwt_identity())

        # 获取学生已选课程
        courses = Course.query.join(CourseStudents).filter(
            CourseStudents.student_id == user_id
        ).all()

        return Result.success(data={
            'items': [{
                'courseId': course.course_id,
                'courseName': course.course_name,
                'teacherName': course.teacher.real_name,
                'semester': course.semester,
                'classTime': f"{course.start_time.strftime('%H:%M')}-{course.end_time.strftime('%H:%M')}",
                'location': course.location
            } for course in courses]
        })

    except Exception as e:
        print(f"Get student courses error: {str(e)}")
        return Result.error("获取课程列表失败")

@student_course_bp.route('/available', methods=['GET'])
@jwt_required()
def get_available_courses():
    try:
        user_id = int(get_jwt_identity())

        # 获取所有课程
        all_courses = Course.query.all()
        # 获取学生已选课程ID
        selected_course_ids = set(
            cs.course_id for cs in CourseStudents.query.filter_by(student_id=user_id).all()
        )

        return Result.success(data={
            'items': [{
                'courseId': course.course_id,
                'courseName': course.course_name,
                'teacherName': course.teacher.real_name,
                'semester': course.semester,
                'classTime': f"{course.start_time.strftime('%H:%M')}-{course.end_time.strftime('%H:%M')}",
                'location': course.location,
                'selected': course.course_id in selected_course_ids
            } for course in all_courses]
        })

    except Exception as e:
        print(f"Get available courses error: {str(e)}")
        return Result.error("获取可选课程失败")

@student_course_bp.route('/select', methods=['POST'])
@jwt_required()
def select_course():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        course_id = data.get('courseId')

        if not course_id:
            return Result.error("缺少课程ID")

        # 检查课程是否存在
        course = Course.query.get_or_404(course_id)

        # 检查是否已选
        if CourseStudents.query.filter_by(
            student_id=user_id,
            course_id=course_id
        ).first():
            return Result.error("已经选择了该课程")

        # 创建选课记录
        course_student = CourseStudents(
            student_id=user_id,
            course_id=course_id
        )
        db.session.add(course_student)
        db.session.commit()

        return Result.success(message="选课成功")

    except Exception as e:
        print(f"Select course error: {str(e)}")
        return Result.error("选课失败")



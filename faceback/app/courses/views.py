from flask import request, Blueprint, current_app, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app import db
from app.courses import course_bp
from app.models.course import Course
from app.models.course_students import CourseStudents
from app.models.user import User
from app.utils.response import Result
from datetime import datetime
import traceback

@course_bp.route('/teacher/courses', methods=['POST'])
@jwt_required()
def create_course():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
             return Result.error("授权用户不存在", code=404)
        if user.role != '教师':
             return Result.error("只有教师才能创建课程", code=403)

        data = request.get_json()
        if not data:
            return Result.error("请求体不能为空", code=400)

        required_fields = ['courseName', 'semester', 'startTime', 'location']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return Result.error(f"缺少或无效的必填字段: {', '.join(missing_fields)}", code=400)

        start_time_str = data['startTime']
        try:
            start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
            end_time_str = Course.get_end_time(start_time_str)
            if not end_time_str:
                current_app.logger.error(f"Failed to calculate end_time for start_time: {start_time_str}")
                return Result.error(f"无法为开始时间 {start_time_str} 计算有效的结束时间", code=400)
            end_time_obj = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError:
             current_app.logger.error(f"Invalid time format received: {start_time_str}")
             return Result.error(f"时间格式错误: '{start_time_str}'，应为 HH:MM", code=400)
        except Exception as time_e:
             current_app.logger.error(f"Error processing time {start_time_str}: {time_e}")
             traceback.print_exc()
             return Result.error(f"处理时间时出错: {time_e}", code=500)

        try:
            course = Course(
                course_name=data['courseName'],
                teacher_id=user_id,
                semester=data['semester'],
                description=data.get('description', ''),
                start_time=start_time_obj,
                end_time=end_time_obj,
                location=data['location']
            )
            db.session.add(course)
            db.session.flush()
            current_app.logger.info(f"Attempting to add course: {course.to_dict()}")
            db.session.commit()
            current_app.logger.info(f"Successfully added course ID: {course.course_id}")
            return Result.success(data=course.to_dict(), message="课程创建成功")

        except IntegrityError as ie:
            db.session.rollback()
            current_app.logger.error(f"Database Integrity Error: {ie}")
            traceback.print_exc()
            return Result.error(f"数据库错误: {ie}", code=409)
        except Exception as db_e:
            db.session.rollback()
            current_app.logger.error(f"Database Error on commit: {db_e}")
            traceback.print_exc()
            return Result.error(f"保存课程到数据库时出错: {db_e}", code=500)

    except Exception as e:
        current_app.logger.error(f"Unexpected error in create_course: {e}")
        traceback.print_exc()
        return Result.error(f"创建课程时发生意外错误: {str(e)}", code=500)

@course_bp.route('/teacher/courses', methods=['GET'])
@jwt_required()
def get_courses():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user: return Result.error("用户不存在", 404)
        if user.role != '教师': return Result.error("无权访问", 403)

        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        keyword = request.args.get('keyword', '')

        query = Course.query.filter_by(teacher_id=user_id)
        if keyword:
            query = query.filter(Course.course_name.ilike(f'%{keyword}%'))

        pagination = query.order_by(Course.created_at.desc()).paginate(page=page, per_page=limit, error_out=False)
        courses = pagination.items
        total = pagination.total

        return Result.success(data={'total': total, 'items': [c.to_dict() for c in courses]})
    except Exception as e:
        current_app.logger.error(f"Error getting teacher courses: {e}")
        traceback.print_exc()
        return Result.error("获取课程列表失败")

@course_bp.route('/teacher/courses/<int:course_id>', methods=['PUT'])
@jwt_required()
def update_course(course_id):
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user: return Result.error("用户不存在", 404)

        course = Course.query.get_or_404(course_id)
        if course.teacher_id != user_id:
            return Result.error("无权修改此课程", code=403)

        data = request.get_json()
        if not data: return Result.error("请求体不能为空", 400)

        required_fields = ['courseName', 'semester', 'startTime', 'location']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return Result.error(f"缺少或无效的必填字段: {', '.join(missing_fields)}", code=400)

        start_time_str = data['startTime']
        try:
            start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
            end_time_str = Course.get_end_time(start_time_str)
            if not end_time_str:
                 current_app.logger.error(f"Update: Failed end_time for start_time: {start_time_str}")
                 return Result.error(f"无法为开始时间 {start_time_str} 计算有效的结束时间", code=400)
            end_time_obj = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError:
             current_app.logger.error(f"Update: Invalid time format: {start_time_str}")
             return Result.error(f"时间格式错误: '{start_time_str}'，应为 HH:MM", code=400)
        except Exception as time_e:
             current_app.logger.error(f"Update: Error processing time {start_time_str}: {time_e}")
             traceback.print_exc()
             return Result.error(f"处理时间时出错: {time_e}", code=500)
        try:
            course.course_name = data['courseName']
            course.semester = data['semester']
            course.description = data.get('description', course.description)
            course.start_time = start_time_obj
            course.end_time = end_time_obj
            course.location = data['location']
            db.session.commit()
            return Result.success(data=course.to_dict(), message="课程更新成功")
        except Exception as db_e:
            db.session.rollback()
            current_app.logger.error(f"Update DB Error: {db_e}")
            traceback.print_exc()
            return Result.error(f"更新课程到数据库时出错: {db_e}", code=500)
    except Exception as e:
        current_app.logger.error(f"Unexpected error in update_course: {e}")
        traceback.print_exc()
        return Result.error(f"更新课程时发生意外错误: {str(e)}", code=500)

@course_bp.route('/teacher/courses/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_course(course_id):
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user: return Result.error("用户不存在", 404)
        course = Course.query.get_or_404(course_id)
        if course.teacher_id != user_id:
            return Result.error("无权删除此课程", code=403)
        try:
            db.session.delete(course)
            db.session.commit()
            return Result.success(message="课程删除成功")
        except Exception as db_e:
            db.session.rollback()
            current_app.logger.error(f"Delete DB Error: {db_e}")
            traceback.print_exc()
            return Result.error(f"删除课程时数据库出错: {db_e}", code=500)
    except Exception as e:
        current_app.logger.error(f"Unexpected error in delete_course: {e}")
        traceback.print_exc()
        return Result.error(f"删除课程时发生意外错误: {str(e)}", code=500)

@course_bp.route('/teacher/courses/<int:course_id>/students', methods=['GET'])
@jwt_required()
def get_students_for_course(course_id):
    try:
        teacher_id = int(get_jwt_identity())
        course = Course.query.get(course_id)
        if not course:
            return Result.error("课程不存在", code=404)
        if course.teacher_id != teacher_id:
            return Result.error("无权查看此课程的学生", code=403)
        students = course.students.all() 
        student_data = []
        for student in students:
             s_dict = student.to_dict()
             s_dict['userId'] = student.user_id
             student_data.append(s_dict)


        # Add pagination later if needed
        return Result.success(data={'items': student_data, 'total': len(student_data)})

    except Exception as e:
        current_app.logger.error(f"Error fetching students for course {course_id}: {e}")
        traceback.print_exc()
        return Result.error("获取学生列表失败")

@course_bp.route('/teacher/courses/<int:course_id>/students/<int:student_id>', methods=['DELETE'])
@jwt_required()
def remove_student(course_id, student_id):
    """Removes a student from a specific course."""
    try:
        teacher_id = int(get_jwt_identity())
        course = Course.query.get(course_id)
        student = User.query.get(student_id)

        if not course: return Result.error("课程不存在", code=404)
        if not student: return Result.error("学生不存在", code=404)
        if student.role != '学生': return Result.error("指定用户不是学生", code=400)

        # Verify teacher owns the course
        if course.teacher_id != teacher_id:
            return Result.error("无权修改此课程的学生列表", code=403)

        # Check if student is actually in the course
        if student not in course.students:
            return Result.error("该学生未选修此课程", code=400)

        # Remove the student using the relationship
        course.students.remove(student)
        db.session.commit()
        current_app.logger.info(f"Teacher {teacher_id} removed student {student_id} from course {course_id}")
        return Result.success(message="学生已成功移除")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error removing student {student_id} from course {course_id}: {e}")
        traceback.print_exc()
        return Result.error(f"移除学生失败: {str(e)}")

@course_bp.route('/teacher/courses/<int:course_id>', methods=['GET'])
@jwt_required()
def get_single_course(course_id):
    """Fetches details for a single course owned by the teacher."""
    try:
        teacher_id = int(get_jwt_identity())
        course = Course.query.get(course_id)

        if not course:
            return Result.error("课程不存在", code=404)

        # Verify teacher ownership
        if course.teacher_id != teacher_id:
             return Result.error("无权查看此课程", code=403)

        return Result.success(data=course.to_dict())

    except Exception as e:
        current_app.logger.error(f"Error fetching course {course_id}: {e}")
        traceback.print_exc()
        return Result.error("获取课程详情失败")

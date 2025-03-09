from flask import request, Blueprint, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import or_

from app import db
from app.courses import course_bp
from app.models.course import Course
from app.models.course_students import CourseStudents
from app.models.user import User
from app.utils.response import Result
from datetime import datetime

@course_bp.route('/add', methods=['POST'])
@jwt_required()
def create_course():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # 验证必填字段
        required_fields = ['courseName', 'semester', 'startTime', 'location']
        for field in required_fields:
            if field not in data:
                return Result.error(f"缺少必填字段: {field}")

        # 获取对应的下课时间
        end_time = Course.get_end_time(data['startTime'])
        if not end_time:
            return Result.error("无效的上课时间")

        # 创建课程
        course = Course(
            course_name=data['courseName'],
            teacher_id=user_id,
            semester=data['semester'],
            description=data.get('description', ''),
            start_time=datetime.strptime(data['startTime'], '%H:%M').time(),
            end_time=datetime.strptime(end_time, '%H:%M').time(),
            location=data['location']
        )

        db.session.add(course)
        db.session.commit()

        return Result.success(message="课程创建成功")

    except Exception as e:
        print(f"Create course error: {str(e)}")
        return Result.error("创建课程失败")

@course_bp.route('/listpage', methods=['GET'])
@jwt_required()
def get_courses():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        keyword = request.args.get('keyword', '')

        # 构建查询
        if user.role == '教师' or user.role =='管理员':
            # 教师查看自己创建的课程
            query = Course.query.filter_by(teacher_id=user_id)
        else:
            # 学生查看已选课程
            # 使用 course_students 关联表进行查询
            query = Course.query.join(
                CourseStudents,
                Course.course_id == CourseStudents.course_id
            ).filter(CourseStudents.student_id == user_id)

        # 添加搜索条件
        if keyword:
            query = query.filter(Course.course_name.like(f'%{keyword}%'))

        # 执行分页查询
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        courses = pagination.items

        # 使用 Result 类封装返回数据
        return Result.success(data={
            'total': pagination.total,
            'items': [{
                'courseId': c.course_id,
                'courseName': c.course_name,
                'semester': c.semester,
                'startTime': c.start_time.strftime('%H:%M') if c.start_time else None,
                'endTime': c.end_time.strftime('%H:%M') if c.end_time else None,
                'location': c.location,
                'description': c.description
            } for c in courses]
        })

    except Exception as e:
        print(f"Get courses error: {str(e)}")
        # 在开发环境打印详细错误信息
        import traceback
        traceback.print_exc()
        return Result.error("获取课程列表失败")

@course_bp.route('/<int:course_id>', methods=['PUT'])
@jwt_required()
def update_course(course_id):
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
 
        course = Course.query.get_or_404(course_id)
        print(user_id)
        print(course.teacher_id)
        if course.teacher_id != user_id:
            return Result.error("无权修改此课程", code=403)
 
        required_fields = ['courseName', 'semester', 'startTime', 'location']
        for field in required_fields:
            if field not in data:
                return Result.error(f"缺少必填字段: {field}")
 
        end_time = Course.get_end_time(data['startTime'])
        if not end_time:
            return Result.error("无效的上课时间")
 
        course.course_name = data['courseName']
        course.semester = data['semester']
        course.description = data.get('description', '')
        course.start_time = datetime.strptime(data['startTime'], '%H:%M').time()
        course.end_time = datetime.strptime(end_time, '%H:%M').time()
        course.location = data['location']

        db.session.commit()
        return Result.success(message="课程更新成功")

    except Exception as e:
        print(f"Update course error: {str(e)}")
        return Result.error("更新课程失败")

@course_bp.route('/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_course(course_id):
    try:
        user_id = int(get_jwt_identity())

        # 获取课程并验证权限
        course = Course.query.get_or_404(course_id)
        if course.teacher_id != user_id:
            return Result.error("无权删除此课程", code=403)

        # 删除课程
        db.session.delete(course)
        db.session.commit()

        return Result.success(message="课程删除成功")

    except Exception as e:
        print(f"Delete course error: {str(e)}")
        return Result.error("删除课程失败")

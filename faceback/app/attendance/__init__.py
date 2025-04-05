from flask import Blueprint


teacher_attendance_bp = Blueprint('api/teacher/attendance', __name__)

attendance_bp = Blueprint('attendance', __name__)

from . import views

# 初始化定时任务
def init_scheduler(app):
    """初始化自动结束任务的定时器"""
    with app.app_context():
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.interval import IntervalTrigger
        import atexit
        from .views import check_and_end_expired_tasks
        
        scheduler = BackgroundScheduler()
        # 每5分钟检查一次过期任务
        scheduler.add_job(
            func=check_and_end_expired_tasks,
            trigger=IntervalTrigger(minutes=5),
            id='check_expired_tasks',
            name='Check and end expired attendance tasks',
            replace_existing=True
        )
        scheduler.start()
        
        # 确保应用退出时关闭定时器
        atexit.register(lambda: scheduler.shutdown())
        
        print("签到任务自动结束定时器已启动")

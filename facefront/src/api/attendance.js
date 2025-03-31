import request from '@/utils/request'
 
export function getTeacherCourses() {
  return request({
    url: '/api/course/listpage',
    method: 'get'
  })
}
 
export function createAttendanceTask(data) {
  return request({
    url: '/api/teacher/attendance/tasks',
    method: 'post',
    data
  })
}
 
export function getAttendanceTasks(params) {
  return request({
    url: '/api/teacher/attendance/tasks',
    method: 'get',
    params
  })
}

export function endAttendanceTask(taskId) {
  return request({
    url: `/api/teacher/attendance/tasks/${taskId}/end`,
    method: 'put'
  })
}

// 获取签到详情
export function getTaskRecords(taskId) {
  return request({
    url: `/api/teacher/attendance/tasks/${taskId}/records`,
    method: 'get'
  })
}

// 获取当前可签到的任务
export function getActiveAttendanceTasks() {
  return request({
    url: '/api/stu/attendance/active',
    method: 'get'
  })
}

// 获取签到历史记录
export function getAttendanceHistory() {
  return request({
    url: '/api/stu/attendance/history',
    method: 'get'
  })
}

// 提交签到  人脸
export function submitAttendance(data) {
  // 确保data是一个FormData对象
  if (!(data instanceof FormData)) {
    console.error('submitAttendance期望接收FormData对象');
    return Promise.reject(new Error('无效的数据格式'));
  }

  return request({
    url: '/api/stu/attendance/sign',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
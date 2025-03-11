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

// 提交签到
export function submitAttendance(data) {
  return request({
    url: '/api/stu/attendance/checkin',
    method: 'post',
    data
  })
}
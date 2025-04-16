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

// 提交签到（确保正确处理FormData对象）
export function submitAttendance(formData) {
  return request({
    url: '/api/stu/attendance/sign',
    method: 'post',
    data: formData,
    headers: {
      // 关键修改：不要显式设置Content-Type，让浏览器自动设置，包括boundary
      // 'Content-Type': 'multipart/form-data'
    },
    // 确保不会自动转换或处理FormData
    transformRequest: [function(data) {
      return data; // 不做任何转换，直接使用原始FormData
    }]
  })
}

// //  进行查看签到的图片
// export function getStudentFaceImage(recordId) {
//   return request({
//     url: `/api/teacher/attendance/records/${recordId}/face`,
//     method: 'get'
//   })
// }

// 学生提交申诉
export function submitAppeal(data) {
  return request({
    url: '/api/stu/attendance/appeal',
    method: 'post',
    data
  })
}

// 学生获取申诉记录
export function getStudentAppeals() {
  return request({
    url: '/api/stu/attendance/appeals',
    method: 'get'
  })
}

// 教师获取待审核申诉
export function getAppeals() {
  return request({
    url: '/api/teacher/attendance/appeals',
    method: 'get'
  })
}

// 教师审核申诉
export function reviewAppeal(recordId, data) {
  return request({
    url: `/api/teacher/attendance/appeals/${recordId}/review`,
    method: 'post',
    data
  })
}

// --- New Statistics API Functions ---

// 获取教师课程签到率统计
export function getCourseAttendanceRates(params) {
  return request({
    url: '/api/teacher/attendance/stats/course-rates',
    method: 'get',
    params // Pass courseId filter if needed
  })
}

// 获取指定任务的学生签到详情
export function getTaskAttendanceDetails(taskId) {
  return request({
    url: `/api/teacher/attendance/stats/task-details/${taskId}`,
    method: 'get'
  })
}

// --- End of New Statistics API Functions ---
import request from '@/utils/request'

// 获取所有课程 (可能用于管理员 - Adjust URL if needed)
export function getAllCourses(params) {
  return request({
    url: '/api/courses', // Assuming this might be a different blueprint/prefix
    method: 'get',
    params,
  })
}

// 获取教师的课程列表
export function getTeacherCourses(params) {
  return request({
    url: '/api/course/teacher/courses', // Keep this as is
    method: 'get',
    params,
  })
}

// 获取学生的课程列表 (Enrolled Courses)
export function getStudentCourses(params) {
  return request({
    url: '/api/stu/course/courses', // <--- CORRECTED URL (Matches backend prefix + route)
    method: 'get',
    params,
  })
}

// 创建课程 (教师)
export function createCourse(data) {
  return request({
    url: '/api/course/teacher/courses', // Keep this as is
    method: 'post',
    data,
  })
}

// 更新课程 (教师)
export function updateCourse(courseId, data) {
  return request({
    url: `/api/course/teacher/courses/${courseId}`, // <--- CORRECTED URL
    method: 'put',
    data,
  })
}

// 删除课程 (教师)
export function deleteCourse(courseId) {
  return request({
    url: `/api/course/teacher/courses/${courseId}`, // <--- CORRECTED URL
    method: 'delete',
  })
}

// 获取课程详情 (通用 - Adjust URL if needed)
export function getCourseDetails(courseId) {
  return request({
    url: `/api/courses/${courseId}`, // Assuming this might be a different blueprint/prefix
    method: 'get',
  })
}

// 获取课程学生列表 (教师)
export function getCourseStudents(courseId, params) {
  return request({
    url: `/api/course/teacher/courses/${courseId}/students`, // <--- CORRECTED URL
    method: 'get',
    params,
  })
}

// 添加学生到课程 (教师)
export function addStudentToCourse(courseId, data) {
  return request({
    url: `/api/course/teacher/courses/${courseId}/students`, // <--- CORRECTED URL
    method: 'post',
    data,
  })
}

// 从课程移除学生 (教师)
export function removeStudentFromCourse(courseId, studentId) {
  return request({
    url: `/api/course/teacher/courses/${courseId}/students/${studentId}`, // <--- CORRECTED URL
    method: 'delete',
  })
}

// --- STUDENT COURSE APIs ---

// 获取可选课程 (Available Courses for Student)
export function getAvailableCourses(params) {
  return request({
    url: '/api/stu/course/available', // <--- CORRECTED URL
    method: 'get',
    params
  })
}

// 选课 (Student Selects Course)
export function selectCourse(courseId) {
  return request({
    url: '/api/stu/course/select', // <--- CORRECTED URL
    method: 'post',
    data: { courseId }
  })
}

// 学生加入课程 (If different from select)
export function joinCourse(data) {
    return request({
        url: '/api/stu/course/join', // <--- CORRECTED URL (Verify backend route)
        method: 'post',
        data
    })
}

// 学生退出课程
export function leaveCourse(courseId) {
    return request({
        url: `/api/stu/course/${courseId}/leave`, // <--- CORRECTED URL (Verify backend route)
        method: 'post' // Or DELETE? Verify backend method
    })
}

// --- OTHER APIs (Teacher Course Mgmt, Attendance, etc. - unchanged) ---

// // 获取可选课程 (Student)
// export function getAvailableCourses() {
//   // Example: Assuming student blueprint prefix is /api/student
//   return request({
//     url: '/api/student/courses/available', // Check this route in student views
//     method: 'get'
//   })
// }

// // 选课 (Student)
// export function selectCourse(courseId) {
//   // Example: Assuming student blueprint prefix is /api/student
//   return request({
//     url: '/api/student/courses/select', // Check this route in student views
//     method: 'post',
//     data: { courseId }
//   })
// } 
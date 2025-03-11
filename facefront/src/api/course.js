import request from '@/utils/request'

// 创建课程
export function createCourse(data) {
  return request({
    url: '/api/course/add',
    method: 'post',
    data
  })
}

// 获取课程列表（带分页和搜索）
export function getCourses(params) {
  return request({
    url: '/api/course/listpage',
    method: 'get',
    params
  })
}

// 更新课程
export function updateCourse(id, data) {
  return request({
    url: `/api/course/${id}`,
    method: 'put',
    data
  })
}

// 删除课程
export function deleteCourse(id) {
  return request({
    url: `/api/course/${id}`,
    method: 'delete'
  })
}

// 获取学生已选课程
export function getStudentCourses() {
  return request({
    url: '/api/stu/course/list',
    method: 'get'
  })
}

// 获取可选课程
export function getAvailableCourses() {
  return request({
    url: '/api/stu/course/available',
    method: 'get'
  })
}

// 选课
export function selectCourse(courseId) {
  return request({
    url: '/api/stu/course/select',
    method: 'post',
    data: { courseId }
  })
} 
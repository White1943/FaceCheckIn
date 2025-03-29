import request from '@/utils/request'

export function getList(data) {
  return request({
    url: '/personalCenter/getList',
    method: 'post',
    data,
  })
}

export function doEdit(data) {
  return request({
    url: '/personalCenter/doEdit',
    method: 'post',
    data,
  })
}

export function doDelete(data) {
  return request({
    url: '/personalCenter/doDelete',
    method: 'post',
    data,
  })
}

// 获取个人信息
export function getPersonalInfo() {
  return request({
    url: '/api/personal/info',
    method: 'get'
  })
}

// 更新个人信息
export function updatePersonalInfo(data) {
  return request({
    url: '/api/personal/info',
    method: 'put',
    data
  })
}
// 更新头像
export function updateAvatar(formData) {
  return request({
    url: '/api/personal/avatar',
    method: 'post',
    data: formData,
    // 关键点1: 不要转换FormData对象
    transformRequest: [function (data) {
      return data; // 直接返回FormData对象，不做任何处理
    }],
    headers: {
      // 关键点2: 不要手动设置Content-Type，让浏览器自动处理
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取头像
export function getAvatar(avatarPath) {
  return request({
    url: `/api/personal/avatar/${avatarPath}`,
    method: 'get',
    responseType: 'blob'  // 重要：设置响应类型为blob
  })
}
// 修改密码
export function changePassword(data) {
  return request({
    url: '/api/personal/password',
    method: 'put',
    data
  })
}

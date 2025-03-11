import request from '@/utils/request'
import { encryptedData } from '@/utils/encrypt'
import { loginRSA } from '@/config'

export async function login(data) {
  if (loginRSA) {
    data = await encryptedData(data)
  }
  return request({
    url: '/api/auth/login',
    method: 'post',
    data,
  })
}

export function register(data) {
  return request({
    url: '/api/auth/register',
    method: 'post',
    data,
  })
}

export function getUserInfo() {
  return request({
    url: '/api/auth/profile',
    method: 'get',
  })
}

export function logout() {
  return request({
    url: '/api/auth/logout',
    method: 'post',
  })
}

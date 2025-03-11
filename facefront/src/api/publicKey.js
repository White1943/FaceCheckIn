import request from '@/utils/request'

export function getPublicKey() {
  return request({
    url: '/api/auth/public-key',
    method: 'get'
  })
}

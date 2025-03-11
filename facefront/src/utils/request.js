import Vue from 'vue'
import axios from 'axios'
import { getAccessToken } from '@/utils/accessToken'
import {
  baseURL,
  contentType,
  debounce,
  invalidCode,
  loginInterception,
  noPermissionCode,
  requestTimeout,
  successCode,
  tokenName,
} from '@/config'
import store from '@/store'
import qs from 'qs'
import router from '@/router'
import { isArray } from '@/utils/validate'

let loadingInstance

/**
 * @author https://github.com/zxwk1998/vue-admin-better （不想保留author可删除）
 * @description 处理code异常
 * @param {*} code
 * @param {*} msg
 */
const handleCode = (code, msg) => {
  switch (code) {
    case invalidCode:
      Vue.prototype.$baseMessage(msg || `后端接口${code}异常`, 'error')
      store.dispatch('user/resetAccessToken').catch(() => {})
      if (loginInterception) {
        location.reload()
      }
      break
    case noPermissionCode:
      router.push({ path: '/401' }).catch(() => {})
      break
    default:
      Vue.prototype.$baseMessage(msg || `后端接口${code}异常`, 'error')
      break
  }
}

const instance = axios.create({
  baseURL,
  timeout: requestTimeout,
  headers: {
    'Content-Type': contentType,
  },
})

instance.interceptors.request.use(
  (config) => {
    const token = getAccessToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    // 移除加密相关代码，直接发送原始数据
    if (config.data) {
      config.data = Vue.prototype.$baseLodash.pickBy(config.data, Vue.prototype.$baseLodash.identity)
    }
    
    if (config.data && config.headers['Content-Type'] === 'application/x-www-form-urlencoded;charset=UTF-8')
      config.data = qs.stringify(config.data)
    if (debounce.some((item) => config.url.includes(item))) loadingInstance = Vue.prototype.$baseLoading()
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

instance.interceptors.response.use(
  (response) => {
    if (loadingInstance) loadingInstance.close()

    const { data, config } = response
    const { code, message, data: responseData } = data

    // 操作正常Code数组
    const codeVerificationArray = isArray(successCode) ? [...successCode] : [...[successCode]]
    
    // 是否操作正常
    if (codeVerificationArray.includes(code)) {
      return data
    } else {
      Vue.prototype.$baseMessage(message || `请求失败`, 'error')
      return Promise.reject(
        `请求失败:${JSON.stringify({
          url: config.url,
          code,
          message,
        })}` || 'Error'
      )
    }
  },
  (error) => {
    if (loadingInstance) loadingInstance.close()
    
    if (error.response && error.response.data) {
      const { message } = error.response.data
      Vue.prototype.$baseMessage(message || '请求失败', 'error')
    } else {
      let { message } = error
      if (message === 'Network Error') {
        message = '后端接口连接异常'
      }
      if (message.includes('timeout')) {
        message = '后端接口请求超时'
      }
      if (message.includes('Request failed with status code')) {
        message = '请求失败'
      }
      Vue.prototype.$baseMessage(message || `后端接口未知异常`, 'error')
    }
    return Promise.reject(error)
  }
)

export default instance

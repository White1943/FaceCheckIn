/**
 * @author https://github.com/zxwk1998/vue-admin-better （不想保留author可删除）
 * @description 登录、获取用户信息、退出登录、清除accessToken逻辑，不建议修改
 */

import Vue from 'vue'
import { getUserInfo, login, logout } from '@/api/user'
import { getAccessToken, removeAccessToken, setAccessToken } from '@/utils/accessToken'
import { resetRouter } from '@/router'
import { title, tokenName } from '@/config'
import { defaultAvatar } from '@/config/settings'

// 保存用户头像信息的键
const USER_AVATAR_KEY = 'user_avatar'

// 后端API基础URL
const API_BASE_URL = 'http://localhost:5001'

const state = {
  accessToken: getAccessToken(),
  username: '',
  avatar: localStorage.getItem(USER_AVATAR_KEY) || defaultAvatar,
  permissions: [], // 用户权限
}
const getters = {
  accessToken: (state) => state.accessToken,
  username: (state) => state.username,
  avatar: (state) => state.avatar,
  permissions: (state) => state.permissions,
}
const mutations = {
  setAccessToken(state, accessToken) {
    state.accessToken = accessToken
    setAccessToken(accessToken)
  },
  setUsername(state, username) {
    state.username = username
  },
  setAvatar(state, avatar) {
    // 处理头像路径
    if (avatar && !avatar.startsWith('http') && !avatar.startsWith('data:')) {
      // 构建完整的头像URL
      const fullAvatarUrl = `${API_BASE_URL}${avatar}`
      state.avatar = fullAvatarUrl
      // 保存到localStorage，以便页面刷新后恢复
      localStorage.setItem(USER_AVATAR_KEY, fullAvatarUrl)
    } else {
      state.avatar = avatar || defaultAvatar
      localStorage.setItem(USER_AVATAR_KEY, avatar || defaultAvatar)
    }
  },
  setPermissions(state, permissions) {
    state.permissions = permissions
  },
}
const actions = {
  setPermissions({ commit }, permissions) {
    commit('setPermissions', permissions)
  },
  async login({ commit }, userInfo) {
    const { data } = await login(userInfo)
    const accessToken = data.token  // 这里期望后端返回 { token: 'xxx' }
    commit('setAccessToken', accessToken)
    setAccessToken(accessToken)
  },
  async getUserInfo({ commit }) {
    const { data } = await getUserInfo()
    let permissions = ['student'] 
    
    switch (data.role) {
      case '教师':
        permissions = ['teacher']
        break
      case '管理员':
        permissions = ['admin']
        break
      case '学生':
        permissions = ['student']
        break
      default:
        permissions = ['student']
    }
    
    commit('setPermissions', permissions)
    commit('setUsername', data.username)
    commit('setAvatar', data.avatar)
    
    return permissions
  },
  async logout({ dispatch }) {
    await logout(state.accessToken)
    await dispatch('resetAccessToken')
    await resetRouter()
    // 清除头像缓存
    localStorage.removeItem(USER_AVATAR_KEY)
  },
  resetAccessToken({ commit }) {
    commit('setPermissions', [])
    commit('setAccessToken', '')
    removeAccessToken()
    // 清除头像缓存
    localStorage.removeItem(USER_AVATAR_KEY)
  },
}
export default { state, getters, mutations, actions }

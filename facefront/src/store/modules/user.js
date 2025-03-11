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

// const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const state = {
  accessToken: getAccessToken(),
  username: '',
  avatar: defaultAvatar,
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
    state.avatar = avatar
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
    commit('setAvatar', data.avatar )
    
    return permissions
  },
  async logout({ dispatch }) {
    await logout(state.accessToken)
    await dispatch('resetAccessToken')
    await resetRouter()
  },
  resetAccessToken({ commit }) {
    commit('setPermissions', [])
    commit('setAccessToken', '')
    removeAccessToken()
  },
}
export default { state, getters, mutations, actions }

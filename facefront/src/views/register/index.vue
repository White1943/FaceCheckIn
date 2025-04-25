<template>
  <div class="register-container">
    <el-row>
      <el-col :lg="16" :md="12" :sm="24" :xl="16" :xs="24">
        <div style="color: transparent">占位符</div>
      </el-col>
      <el-col :lg="8" :md="12" :sm="24" :xl="8" :xs="24">
        <el-form ref="registerForm" :model="registerForm" :rules="registerRules" class="register-form">
          <h3 class="title">{{ $baseTitle }} 注册</h3>
          
          <el-form-item prop="username">
            <el-input
              v-model="registerForm.username"
              placeholder="请输入用户名"
              type="text">
              <vab-icon slot="prefix" :icon="['fas', 'user']" />
            </el-input>
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              placeholder="请输入密码"
              type="password">
              <vab-icon slot="prefix" :icon="['fas', 'lock']" />
            </el-input>
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              placeholder="请确认密码"
              type="password">
              <vab-icon slot="prefix" :icon="['fas', 'lock']" />
            </el-input>
          </el-form-item>

          <el-form-item prop="realName">
            <el-input
              v-model="registerForm.realName"
              placeholder="请输入真实姓名"
              type="text">
              <vab-icon slot="prefix" :icon="['fas', 'user']" />
            </el-input>
          </el-form-item>

          <el-form-item prop="role">
            <el-select v-model="registerForm.role" placeholder="请选择角色">
              <el-option label="学生" value="学生" />
              <el-option label="教师" value="教师" />
              <el-option label="管理员" value="管理员"/>
            </el-select>
          </el-form-item>

          <el-form-item prop="email">
            <el-input
              v-model="registerForm.email"
              placeholder="请输入邮箱（选填）"
              type="email">
              <vab-icon slot="prefix" :icon="['fas', 'envelope']" />
            </el-input>
          </el-form-item>

          <el-button :loading="loading" type="primary" @click.native.prevent="handleRegister">
            注册
          </el-button>
          <router-link to="/login">
            <div style="margin-top: 20px">已有账号？立即登录</div>
          </router-link>
        </el-form>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { register } from '@/api/user'
import { isPassword } from '@/utils/validate'

export default {
  name: 'SysRegister',
  data() {
    const validatePassword = (rule, value, callback) => {
      if (!isPassword(value)) {
        callback(new Error('密码不能少于6位'))
      } else {
        callback()
      }
    }
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.registerForm.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    return {
      registerForm: {
        username: '',
        password: '',
        confirmPassword: '',
        realName: '',
        role: '',
        email: '',
      },
      registerRules: {
        username: [{ required: true, trigger: 'blur', message: '请输入用户名' }],
        password: [{ required: true, trigger: 'blur', validator: validatePassword }],
        confirmPassword: [{ required: true, trigger: 'blur', validator: validateConfirmPassword }],
        realName: [{ required: true, trigger: 'blur', message: '请输入真实姓名' }],
        role: [{ required: true, trigger: 'change', message: '请选择角色' }],
        email: [{ type: 'email', trigger: 'blur', message: '请输入正确的邮箱地址' }],
      },
      loading: false,
    }
  },
  methods: {
    async handleRegister() {
      try {
        await this.$refs.registerForm.validate()
        this.loading = true
        
        const response = await register(this.registerForm)
        this.$baseMessage('注册成功', 'success')
        this.$router.push('/login')
      } catch (error) {
        console.error('注册失败:', error)
        this.$baseMessage(error.message || '注册失败', 'error')
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style lang="scss" scoped>
  .register-container {
    height: 100vh;
    background: url('~@/assets/login_images/background.jpg') center center fixed no-repeat;
    background-size: cover;
    overflow-y: auto;
    padding: 20px 0;

    .title {
      font-size: 42px;
      font-weight: 500;
      color: rgba(14, 18, 26, 1);
      margin-bottom: 30px;
    }

    .title-tips {
      margin-top: 15px;
      font-size: 20px;
      font-weight: 400;
      color: rgba(14, 18, 26, 1);
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .register-btn {
      display: inherit;
      width: 100%;
      height: 45px;
      margin-top: 5px;
      border: 0;

      &:hover {
        opacity: 0.9;
      }
    }

    .register-form {
      position: relative;
      max-width: 520px;
      margin: 50px auto;
      overflow: hidden;

      @media screen and (min-height: 800px) {
        margin-top: 100px;
      }

      .forget-password {
        width: 100%;
        margin-top: 40px;
        text-align: left;
      }

      .per-code {
        width: 100px;
        height: 36px;
        font-size: 20px;
        line-height: 36px;
        color: #fff;
        text-align: center;
        cursor: pointer;
        background: #bbc1ce;
      }

      .phone-code {
        width: 120px;
        height: 36px;
        font-size: 14px;
        color: #fff;
        border-radius: 3px;
      }

      .el-form-item {
        margin-bottom: 20px;
      }

      .el-select {
        width: 100%;
      }
    }

    .tips {
      margin-bottom: 10px;
      font-size: $base-font-size-default;
      color: $base-color-white;

      span {
        &:first-of-type {
          margin-right: 16px;
        }
      }
    }

    .title-container {
      position: relative;

      .title {
        margin: 0 auto 40px auto;
        font-size: 34px;
        font-weight: bold;
        color: $base-color-blue;
        text-align: center;
      }
    }

    .svg-container {
      position: absolute;
      top: 14px;
      left: 15px;
      z-index: $base-z-index;
      font-size: 16px;
      color: #d7dee3;
      cursor: pointer;
      user-select: none;
    }

    .show-pwd {
      position: absolute;
      top: 14px;
      right: 25px;
      font-size: 16px;
      color: $base-font-color;
      cursor: pointer;
      user-select: none;
    }

    ::v-deep {
      .el-form-item {
        padding-right: 0;
        margin: 20px 0;
        color: #454545;
        background: transparent;
        border: 1px solid transparent;
        border-radius: 2px;

        &__content {
          min-height: $base-input-height;
          line-height: $base-input-height;
        }

        &__error {
          position: absolute;
          top: 100%;
          left: 18px;
          font-size: $base-font-size-small;
          line-height: 18px;
          color: $base-color-red;
        }
      }

      .el-input {
        box-sizing: border-box;

        .el-input__count {
          .el-input__count-inner {
            background: transparent;
          }
        }

        .el-input__prefix {
          left: 15px;
          line-height: 56px;

          .svg-inline--fa {
            width: 20px;
          }
        }

        input {
          height: 58px;
          padding-left: 45px;
          font-size: $base-font-size-default;
          line-height: 58px;
          color: $base-font-color;
          background: #f6f4fc;
          border: 0;
          caret-color: $base-font-color;
        }
      }
    }
  }
</style>

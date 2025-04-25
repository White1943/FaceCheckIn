<template>
  <div class="personal-center">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>头像设置</span>
      </div>
 


      <div class="avatar-section">
        <div v-if="userInfo.avatar" class="current-avatar">
          <span>当前头像：</span>
          <img :src="userInfo.avatar" class="avatar-image">
        </div>
        
        <el-upload
          ref="upload"
          action="#"
          :auto-upload="false"
          list-type="picture-card"
          :file-list="fileList"
          :limit="1"
          :on-change="handleFileChange"
          :on-preview="handlePicturePreview"
          :on-remove="handleRemove">
          <i class="el-icon-plus"></i>
        </el-upload>
        
        <el-dialog :visible.sync="dialogVisible">
          <img width="100%" :src="dialogImageUrl" alt="">
        </el-dialog>
        
        <div class="upload-actions">
          <el-button type="primary" :disabled="fileList.length === 0" @click="uploadAvatar">
            上传头像
          </el-button>
          <div class="upload-tip">支持jpg、png格式，大小不超过2MB</div>
        </div>
      </div>
    </el-card>

    <el-card class="box-card" style="margin-top: 20px;">
      <div slot="header" class="clearfix">
        <span>个人信息</span>
      </div>
      
      <el-form ref="userForm" :model="userInfo" :rules="rules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userInfo.username" disabled></el-input>
        </el-form-item>

        <el-form-item label="角色" prop="role">
          <el-input v-model="userInfo.role" disabled></el-input>
        </el-form-item>

        <el-form-item label="姓名" prop="name">
          <el-input v-model="userInfo.name"></el-input>
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userInfo.email"></el-input>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitInfo">保存个人信息</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="box-card" style="margin-top: 20px;">
      <div slot="header" class="clearfix">
        <span>修改密码</span>
      </div>
      
      <el-form ref="passwordForm" :model="passwordForm" :rules="passwordRules" label-width="100px">
        <el-form-item label="原密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password"></el-input>
        </el-form-item>

        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password"></el-input>
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password"></el-input>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitPasswordForm">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'
import { getPersonalInfo, updatePersonalInfo, updateAvatar, changePassword } from '@/api/personalCenter'
import { getAccessToken } from '@/utils/accessToken'

export default {
  name: 'PersonalCenter',
  data() {
    const validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入密码'))
      } else {
        if (this.passwordForm.confirmPassword !== '') {
          this.$refs.passwordForm.validateField('confirmPassword')
        }
        callback()
      }
    }
    const validatePass2 = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== this.passwordForm.newPassword) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }

    return {
      userInfo: {
        username: '',
        role: '',
        name: '',
        email: '',
        avatar: ''
      },
      selectedFile: null,
      passwordForm: {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      rules: {
        name: [
          { required: true, message: '请输入姓名', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ]
      },
      passwordRules: {
        oldPassword: [
          { required: true, message: '请输入原密码', trigger: 'blur' }
        ],
        newPassword: [
          { required: true, validator: validatePass, trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, validator: validatePass2, trigger: 'blur' }
        ]
      },
      uploadUrl: '/api/personal/avatar',
      uploadHeaders: {
        Authorization: `Bearer ${getAccessToken()}`
      },
      imageUrl: '',
      fileList: [],
      fileParam: null,
      dialogImageUrl: '',
      dialogVisible: false
    }
  },
  created() {
    this.getUserInfo()
  },
  methods: {
    async getUserInfo() {
      try {
        const res = await getPersonalInfo()
        if (res.code === 200) {
          this.userInfo = {
            username: res.data.username,
            role: res.data.role,
            name: res.data.name,
            email: res.data.email,
            avatar: res.data.avatar
          }
          
          // 为头像URL添加baseURL前缀，确保图片能正确显示
          if (this.userInfo.avatar && !this.userInfo.avatar.startsWith('http')) {
            const baseURL = 'http://localhost:5001'; // 使用配置中的URL
            this.userInfo.avatar = baseURL + this.userInfo.avatar;
          }
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
        this.$message.error('获取用户信息失败')
      }
    },
    async submitInfo() {
      try {
        await this.$refs.userForm.validate()
        
        const infoData = {
          name: this.userInfo.name,
          email: this.userInfo.email
        }
        
        const result = await updatePersonalInfo(infoData)
        if (result.code === 200) {
          this.$message.success('个人信息更新成功')
          
          // 更新显示信息
          this.userInfo = {
            ...this.userInfo,
            name: result.data.name,
            email: result.data.email
          }
        } else {
          this.$message.error(result.message || '个人信息更新失败')
        }
      } catch (error) {
        console.error('个人信息更新失败:', error)
        this.$message.error(`个人信息更新失败: ${error.message || '未知错误'}`)
      }
    },
    async submitPasswordForm() {
      try {
        await this.$refs.passwordForm.validate()
        const res = await changePassword(this.passwordForm)
        if (res.code === 200) {
          this.$message.success('密码修改成功')
          this.passwordForm = {
            oldPassword: '',
            newPassword: '',
            confirmPassword: ''
          }
        }
      } catch (error) {
        console.error('修改密码失败:', error)
        this.$message.error('修改密码失败')
      }
    },
    handleFileChange(file, fileList) {
      this.fileList = fileList;
      
      // 创建FormData对象
      if (file.raw) {
        // 检查文件大小
        if (file.raw.size > 2 * 1024 * 1024) {
          this.$message.error('图片大小不能超过2MB');
          this.fileList = [];
          this.fileParam = null;
          return;
        }
        
        this.fileParam = new FormData();
        this.fileParam.append('avatar', file.raw);
      }
    },
    handlePicturePreview(file) {
      this.dialogImageUrl = file.url || URL.createObjectURL(file.raw);
      this.dialogVisible = true;
    },
    handleRemove(file, fileList) {
      this.fileList = fileList;
      this.fileParam = null;
    },
    uploadAvatar() {
      if (!this.fileParam) {
        this.$message.warning('请先选择图片');
        return;
      }
      
      const loading = this.$loading({
        lock: true,
        text: '上传中...',
        spinner: 'el-icon-loading',
      });
      
      // 打印检查FormData内容
      console.log('准备上传的FormData:');
      for (let pair of this.fileParam.entries()) {
        console.log(pair[0], pair[1]);
      }
      
      // 关键修改：使用网络配置中定义的baseURL
      const baseURL = 'http://localhost:5001'; // 直接使用配置文件中的URL
      const url = `${baseURL}/api/personal/avatar`;
      
      axios.post(url, this.fileParam, {
        headers: {
          'Authorization': `Bearer ${getAccessToken()}`,
        }
      }).then(response => {
        if (response.data.code === 200) {
          this.$message.success('头像上传成功');
          // 更新头像URL - 添加baseURL前缀
          this.userInfo.avatar = baseURL + response.data.data.avatar;
          // 更新Vuex中的头像
          this.$store.commit('user/setAvatar', this.userInfo.avatar);
          // 清空文件列表
          this.fileList = [];
          this.fileParam = null;
        } else {
          this.$message.error(response.data.message || '上传失败');
        }
      }).catch(error => {
        console.error('上传错误详情:', error);
        if (error.response) {
          console.error('响应数据:', error.response.data);
        }
        this.$message.error(`上传失败: ${  error.message || '未知错误'}`);
      }).finally(() => {
        loading.close();
      });
    }
  }
}
</script>

<style scoped>
.personal-center {
  padding: 20px;
}
.avatar-section {
  text-align: center;
  padding: 20px;
}
.avatar {
  width: 178px;
  height: 178px;
  display: block;
  margin: 0 auto 20px;
  border-radius: 4px;
  object-fit: cover;
}
.file-input {
  margin-bottom: 10px;
}
.upload-container {
  margin: 20px 0;
}
.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}
.current-avatar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}
.avatar-image {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-left: 10px;
}
.upload-actions {
  margin-top: 20px;
}
</style>

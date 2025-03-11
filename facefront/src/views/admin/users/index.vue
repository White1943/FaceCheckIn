<template>
  <div class="admin-users">
    <el-card>
      <div class="filter-container">
        <el-input
          v-model="searchQuery"
          placeholder="搜索用户"
          style="width: 200px; margin-right: 10px"
        />
        <el-select v-model="roleFilter" placeholder="角色" style="width: 120px; margin-right: 10px">
          <el-option label="全部" value="" />
          <el-option label="教师" value="教师" />
          <el-option label="学生" value="学生" />
          <el-option label="管理员" value="admin" />
        </el-select>
        <el-button type="primary" @click="handleCreate">新建用户</el-button>
      </div>

      <el-table :data="userList" style="width: 100%">
        <el-table-column label="用户名" prop="username" />
        <el-table-column label="真实姓名" prop="realName" />
        <el-table-column label="角色" prop="role" />
        <el-table-column label="邮箱" prop="email" />
        <el-table-column label="状态">
          <template #default="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'">
              {{ scope.row.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="scope">
            <el-button type="text" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button 
              type="text" 
              :style="{ color: scope.row.status === 1 ? '#F56C6C' : '#67C23A' }"
              @click="handleToggleStatus(scope.row)"
            >
              {{ scope.row.status === 1 ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建/编辑用户对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible">
      <el-form ref="userForm" :model="userForm" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" />
        </el-form-item>
        <el-form-item label="真实姓名" prop="realName">
          <el-input v-model="userForm.realName" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role">
            <el-option label="教师" value="教师" />
            <el-option label="学生" value="学生" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'AdminUsers',
  data() {
    return {
      searchQuery: '',
      roleFilter: '',
      userList: [],
      dialogVisible: false,
      dialogTitle: '',
      isEdit: false,
      userForm: {
        username: '',
        password: '',
        realName: '',
        role: '',
        email: ''
      },
      rules: {
        username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
        password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
        realName: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
        role: [{ required: true, message: '请选择角色', trigger: 'change' }],
        email: [{ type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }]
      }
    }
  },
  methods: {
    handleCreate() {
      this.isEdit = false
      this.dialogTitle = '新建用户'
      this.userForm = {
        username: '',
        password: '',
        realName: '',
        role: '',
        email: ''
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.isEdit = true
      this.dialogTitle = '编辑用户'
      this.userForm = { ...row }
      delete this.userForm.password
      this.dialogVisible = true
    },
    handleToggleStatus(row) {
      const action = row.status === 1 ? '禁用' : '启用'
      this.$confirm(`确认${action}该用户?`, '提示', {
        type: 'warning'
      }).then(() => {
        // TODO: 调用更新状态API
        this.$message.success(`${action}成功`)
      })
    },
    handleSubmit() {
      this.$refs.userForm.validate(valid => {
        if (valid) {
          // TODO: 调用创建/更新用户API
          this.$message.success('保存成功')
          this.dialogVisible = false
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.admin-users {
  padding: 20px;

  .filter-container {
    margin-bottom: 20px;
  }
}
</style>

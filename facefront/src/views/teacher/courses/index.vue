<template>
  <div class="teacher-courses">
    <el-card>
      <!-- 搜索区域 -->
      <div class="filter-container">
        <el-input
          v-model="listQuery.keyword"
          placeholder="搜索课程名称"
          style="width: 200px;"
          class="filter-item"
          @keyup.enter.native="handleFilter"
        />
        <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
          搜索
        </el-button>
        <el-button class="filter-item" type="primary" icon="el-icon-plus" @click="handleCreate">
          新建课程
        </el-button>
      </div>

      <!-- 课程列表 -->
      <el-table
        :data="courseList"
        style="width: 100%; margin-top: 20px"
        v-loading="listLoading"
      >
        <el-table-column label="课程名称" prop="courseName" />
        <el-table-column label="学期" prop="semester" />
        <el-table-column label="上课时间">
          <template #default="scope">
            {{ scope.row.startTime }} - {{ scope.row.endTime }}
          </template>
        </el-table-column>
        <el-table-column label="上课地点" prop="location" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="text" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="text" @click="handleDelete(scope.row)">删除</el-button>
            <el-button type="text" @click="handleStudents(scope.row)">学生管理</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          background
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="listQuery.page"
          :page-sizes="[10, 20, 30, 50]"
          :page-size="listQuery.limit"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
        />
      </div>
    </el-card>

    <!-- 新建/编辑课程对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="500px">
      <el-form ref="courseForm" :model="courseForm" :rules="rules" label-width="80px">
        <el-form-item label="课程名称" prop="courseName">
          <el-input v-model="courseForm.courseName" />
        </el-form-item>
        <el-form-item label="学期" prop="semester">
          <el-input v-model="courseForm.semester" />
        </el-form-item>
        <el-form-item label="上课时间" prop="startTime">
          <el-select v-model="courseForm.startTime" placeholder="请选择上课时间">
            <el-option label="08:15" value="08:15" />
            <el-option label="10:05" value="10:05" />
            <el-option label="13:00" value="13:00" />
            <el-option label="15:00" value="15:00" />
            <el-option label="18:00" value="18:00" />
            <el-option label="20:00" value="20:00" />
          </el-select>
        </el-form-item>
        <el-form-item label="上课地点" prop="location">
          <el-input v-model="courseForm.location" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="courseForm.description" type="textarea" />
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
import {
  getTeacherCourses,
  createCourse,
  updateCourse,
  deleteCourse,
  getCourseStudents,
  addStudentToCourse,
  removeStudentFromCourse
} from '@/api/course'
import { getAllUsers } from '@/api/user'

export default {
  name: 'TeacherCourses',
  data() {
    return {
      courseList: [],
      listLoading: false,
      total: 0,
      listQuery: {
        page: 1,
        limit: 10,
        keyword: ''
      },
      dialogVisible: false,
      dialogTitle: '',
      courseForm: {
        courseName: '',
        semester: '',
        startTime: '',
        location: '',
        description: ''
      },
      rules: {
        courseName: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
        semester: [{ required: true, message: '请输入学期', trigger: 'blur' }],
        startTime: [{ required: true, message: '请选择上课时间', trigger: 'change' }],
        location: [{ required: true, message: '请输入上课地点', trigger: 'blur' }]
      }
    }
  },
  created() {
    this.fetchCourses()
  },
  methods: {
    async fetchCourses() {
      this.loading = true
      try {
        const response = await getTeacherCourses({
          // page: this.currentPage,
          // limit: this.pageSize,
          // search: this.searchQuery
        })
        if (response.code === 200) {
          this.courseList = response.data.items
          // this.totalCourses = response.data.total // 如果后端返回总数
        } else {
          this.$message.error(response.message || '获取课程列表失败')
        }
      } catch (error) {
        console.error('获取课程列表失败:', error)
        this.$message.error('获取课程列表失败')
      } finally {
        this.loading = false
      }
    },
    handleFilter() {
      this.listQuery.page = 1
      this.fetchCourses()
    },
    handleSizeChange(val) {
      this.listQuery.limit = val
      this.fetchCourses()
    },
    handleCurrentChange(val) {
      this.listQuery.page = val
      this.fetchCourses()
    },
    handleCreate() {
      this.dialogTitle = '新建课程'
      this.courseForm = {
        courseName: '',
        semester: '',
        startTime: '',
        location: '',
        description: ''
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.dialogTitle = '编辑课程'
      this.courseForm = { ...row }
      this.dialogVisible = true
    },
    async handleDelete(row) {
      try {
        await this.$confirm('确认删除该课程?', '提示', {
          type: 'warning'
        })
        await deleteCourse(row.courseId)
        this.$message.success('删除成功')
        this.fetchCourses()
      } catch (error) {
        console.error('删除课程失败:', error)
      }
    },
    handleStudents(row) {
      this.$router.push(`/teacher/courses/${row.courseId}/students`)
    },
    async handleSubmit() {
      try {
        await this.$refs.courseForm.validate()

        // --- DEBUGGING: Log the data being sent ---
        console.log('Submitting Course Form Data:', JSON.stringify(this.courseForm, null, 2));
        // --- END DEBUGGING ---

        if (this.courseForm.courseId) {
          // Update logic - ensure updateCourse API call is correct
          await updateCourse(this.courseForm.courseId, this.courseForm)
          this.$message.success('更新成功')
        } else {
          // Create logic
          const response = await createCourse(this.courseForm) // Call createCourse API
          // Check backend response structure
          if (response.code === 200) {
             this.$message.success(response.message || '新建课程成功')
          } else {
             this.$message.error(response.message || '新建课程失败')
             // Keep dialog open on failure?
             return; // Prevent closing dialog if needed
          }
        }
        this.dialogVisible = false
        this.fetchCourses() // Refresh list
      } catch (error) {
        // Log the detailed error from the API call if it's an Axios error
        if (error.response) {
          console.error('保存课程失败 - Response:', error.response.data);
          this.$message.error(`保存课程失败: ${error.response.data.message || '服务器错误'}`);
        } else if (error.request) {
           console.error('保存课程失败 - No Response:', error.request);
           this.$message.error('保存课程失败: 未收到服务器响应');
        } else {
           console.error('保存课程失败 - Request Setup Error:', error.message);
           this.$message.error(`保存课程失败: ${error.message}`);
        }
        // Don't log generic error message if already handled above
        // console.error('保存课程失败:', error)
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.teacher-courses {
  padding: 20px;
  
  .filter-container {
    margin-bottom: 20px;
    .filter-item {
      margin-right: 10px;
    }
  }

  .pagination-container {
    margin-top: 20px;
    text-align: right;
  }

  .course-detail {
    .detail-item {
      margin-bottom: 15px;
      .label {
        font-weight: bold;
        margin-right: 10px;
      }
    }
  }
}
</style> 
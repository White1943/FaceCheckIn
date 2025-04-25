<template>
  <div class="course-students-view">
    <el-card>
      <div slot="header" class="card-header">
        <span>学生管理: {{ courseName }}</span>
        <div>
          <el-button style="margin-left: 10px;" type="primary" icon="el-icon-back" @click="goBack">返回课程列表</el-button>
          <el-button type="primary" icon="el-icon-refresh" @click="fetchStudents">刷新</el-button>
        </div>
      </div>

      <el-table v-loading="loading" :data="studentList" style="width: 100%">
        <el-table-column label="头像" width="80" align="center">
          <template slot-scope="scope">
            <el-image
              v-if="scope.row.avatar"
              style="width: 40px; height: 40px; border-radius: 50%; cursor: pointer;"
              :src="getImageUrl(scope.row.avatar)"
              :preview-src-list="[getImageUrl(scope.row.avatar)]"
              fit="cover">
              <div slot="error" class="image-slot">
                <i class="el-icon-picture-outline"></i>
              </div>
              <div slot="placeholder" class="image-slot">
                 <i class="el-icon-loading"></i>
              </div>
            </el-image>
            <el-avatar v-else icon="el-icon-user-solid" :size="40"></el-avatar> <!-- Fallback avatar -->
          </template>
        </el-table-column>
        <el-table-column label="学生姓名" prop="realName" min-width="120" />
        <el-table-column label="用户名" prop="username" min-width="120" />
        <el-table-column label="邮箱" prop="email" min-width="180" />
         <el-table-column label="操作" width="100">
           <template slot-scope="scope">
             <el-button
               type="text"
               style="color: #f56c6c"
               @click="handleRemoveStudent(scope.row)">
               移除
             </el-button>
           </template>
         </el-table-column>
      </el-table>
      <el-empty v-if="!loading && studentList.length === 0" description="该课程暂无学生"></el-empty>
 
       <el-pagination
         style="margin-top: 20px; text-align: right;"
         :current-page="pagination.page"
         :page-sizes="[10, 20, 50, 100]"
         :page-size="pagination.limit"
         layout="total, sizes, prev, pager, next, jumper"
         :total="pagination.total"
         @size-change="handleSizeChange"
         @current-change="handleCurrentChange">
       </el-pagination>

    </el-card>
  </div>
</template>

<script>
// Import the API function to get students for a course
import { getCourseStudents, removeStudentFromCourse, getCourseDetails } from '@/api/course'

export default {
  name: 'TeacherCourseStudents',
  data() {
    return {
      loading: false,
      studentList: [],
      courseName: '',
      courseId: null,
      pagination: {  
        page: 1,
        limit: 10,
        total: 0
      }
    }
  },
  created() {
    if (this.$route.params.courseId) {
      this.courseId = this.$route.params.courseId;
      this.fetchCourseName(); // Fetch course name for the header
      this.fetchStudents();
    } else {
      this.$message.error('未找到课程ID');
      this.goBack();
    }
  },
  methods: {
     async fetchCourseName() {
       try {
         const response = await getCourseDetails(this.courseId);
         if (response.code === 200 && response.data) {
           this.courseName = response.data.courseName;
         } else {
            this.courseName = `课程 ${this.courseId}`;
         }
       } catch (error) {
         console.error('获取课程名称失败:', error);
         this.courseName = `课程 ${this.courseId}`;
       }
     },
    async fetchStudents() {
      if (!this.courseId) return;
      this.loading = true;
      try {
        const params = {
          page: this.pagination.page,
          limit: this.pagination.limit
        };
        const response = await getCourseStudents(this.courseId /*, params */);
        if (response.code === 200 && response.data) {
          this.studentList = response.data.items || response.data;
          this.pagination.total = response.data.total || this.studentList.length;  
        } else {
          this.$message.error(response.message || '获取学生列表失败');
          this.studentList = [];
          // this.pagination.total = 0;
        }
      } catch (error) {
        console.error('获取学生列表失败:', error);
        this.$message.error('获取学生列表失败');
        this.studentList = [];
        // this.pagination.total = 0;
      } finally {
        this.loading = false;
      }
    },
    handleSizeChange(val) { 
      this.pagination.limit = val;
      this.fetchStudents();
    },
    handleCurrentChange(val) {  
      this.pagination.page = val;
      this.fetchStudents();
    },
    async handleRemoveStudent(student) {
       if (!student || !student.userId) {
         this.$message.error('无法移除：学生信息无效');
         return;
       }
       try {
         await this.$confirm(`确认将学生 "${student.realName}" 从课程 "${this.courseName}" 中移除吗?`, '提示', {
           confirmButtonText: '确定移除',
           cancelButtonText: '取消',
           type: 'warning'
         });

         const response = await removeStudentFromCourse(this.courseId, student.userId);
         if (response.code === 200) {
           this.$message.success('学生移除成功');
           this.fetchStudents(); // Refresh the list
         } else {
           this.$message.error(`移除失败: ${response.message}`);
         }
       } catch (error) {
         if (error === 'cancel') {
           this.$message.info('操作已取消');
         } else {
           console.error('移除学生时出错:', error);
           this.$message.error(`移除学生时出错: ${error.message || '请查看控制台'}`);
         }
       }
    },
    getImageUrl(relativePath) {
      if (!relativePath) return null;
      if (relativePath.startsWith('http') || relativePath.startsWith('data:')) {
        return relativePath;
      } else if (relativePath.startsWith('/')) {
        return `http://localhost:5001${relativePath}`; 
      }
      return relativePath;
    },
    goBack() {
      // Navigate back to the teacher's course list or use router history
      this.$router.push({ name: 'TeacherCourses' });
      // Alternatively: this.$router.go(-1);
    },
    // formatJoinDate(dateString) { // Example formatter if needed
    //   if (!dateString) return '-';
    //   try {
    //     return new Date(dateString).toLocaleString();
    //   } catch (e) {
    //     return dateString; // Return original if formatting fails
    //   }
    // }
  }
}
</script>

<style lang="scss" scoped>
.course-students-view {
  padding: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .image-slot {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
    background: #f5f7fa;
    color: #c0c4cc; // Lighter color for placeholder/error icon
    font-size: 20px;
    border-radius: 50%; // Keep the slot circular
  }
   // Ensure el-avatar fallback also looks okay
   .el-avatar {
     background-color: #f5f7fa; // Match image slot background
     color: #c0c4cc;
   }
}
</style> 
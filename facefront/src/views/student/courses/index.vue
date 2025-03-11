<template>
  <div class="student-courses">
    <el-card>
      <div class="filter-container">
        <el-input
          v-model="searchQuery"
          placeholder="搜索课程"
          style="width: 200px"
          class="filter-item"
          @keyup.enter.native="handleFilter"
        />
        <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
          搜索
        </el-button>
      </div>

      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane label="我的课程" name="myCourses">
          <el-table :data="courseList" v-loading="loading">
            <el-table-column label="课程名称" prop="courseName" />
            <el-table-column label="教师" prop="teacherName" />
            <el-table-column label="学期" prop="semester" />
            <el-table-column label="上课时间" prop="classTime" />
            <el-table-column label="上课地点" prop="location" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="选课" name="selectCourse">
          <el-table :data="availableCourseList" v-loading="loading">
            <el-table-column label="课程名称" prop="courseName" />
            <el-table-column label="教师" prop="teacherName" />
            <el-table-column label="学期" prop="semester" />
            <el-table-column label="上课时间" prop="classTime" />
            <el-table-column label="上课地点" prop="location" />
            <el-table-column label="操作">
              <template #default="scope">
                <el-button 
                  type="primary" 
                  size="small"
                  :disabled="scope.row.selected"
                  @click="handleSelect(scope.row)"
                >
                  {{ scope.row.selected ? '已选' : '选课' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { getStudentCourses, getAvailableCourses, selectCourse } from '@/api/course'

export default {
  name: 'StudentCourses',
  data() {
    return {
      searchQuery: '',
      activeTab: 'myCourses',
      courseList: [],
      availableCourseList: [],
      loading: false
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        if (this.activeTab === 'myCourses') {
          const response = await getStudentCourses()
          if (response.code === 200) {
            this.courseList = response.data.items
          }
        } else {
          const response = await getAvailableCourses()
          if (response.code === 200) {
            this.availableCourseList = response.data.items
          }
        }
      } catch (error) {
        console.error('获取课程列表失败:', error)
        this.$message.error('获取课程列表失败')
      } finally {
        this.loading = false
      }
    },
    handleTabChange() {
      this.fetchData()
    },
    handleFilter() {
      this.fetchData()
    },
    async handleSelect(course) {
      try {
        await this.$confirm('确认选择该课程?', '提示', {
          type: 'warning'
        })
        const response = await selectCourse(course.courseId)
        if (response.code === 200) {
          this.$message.success('选课成功')
          this.fetchData()
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('选课失败:', error)
          this.$message.error('选课失败')
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.student-courses {
  padding: 20px;

  .filter-container {
    margin-bottom: 20px;
  }
}
</style> 
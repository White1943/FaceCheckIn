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
        <el-tab-pane label="我的课程" name="enrolled">
          <el-table :data="enrolledCourses" v-loading="loading" empty-text="暂无数据">
            <el-table-column prop="courseName" label="课程名称"></el-table-column>
            <el-table-column prop="teacherName" label="教师"></el-table-column>
            <el-table-column prop="semester" label="学期"></el-table-column>
            <el-table-column label="上课时间">
              <template slot-scope="scope">
                {{ scope.row.startTime || '--' }}
              </template>
            </el-table-column>
            <el-table-column prop="location" label="上课地点"></el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="选课" name="available">
          <el-table :data="availableCourses" v-loading="loading" empty-text="暂无可选课程">
            <el-table-column prop="courseName" label="课程名称"></el-table-column>
            <el-table-column prop="teacherName" label="教师"></el-table-column>
            <el-table-column prop="semester" label="学期"></el-table-column>
            <el-table-column label="上课时间">
              <template slot-scope="scope">
                {{ scope.row.startTime || '--' }}
              </template>
            </el-table-column>
            <el-table-column prop="location" label="上课地点"></el-table-column>
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
      activeTab: 'enrolled',
      enrolledCourses: [],
      availableCourses: [],
      loading: false
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true;
      // --- Prepare query parameters ---
      const queryParams = {
        search: this.searchQuery // Add search query
        // Add pagination params here if needed later:
        // page: this.currentPage,
        // limit: this.pageSize
      };
      // --- End Prepare query parameters ---

      try {
        let response;
        console.log("Fetching data for tab:", this.activeTab, "with params:", queryParams);

        if (this.activeTab === 'enrolled') {
          // --- Pass queryParams to API call ---
          response = await getStudentCourses(queryParams);
        } else { // 'available' tab
          // --- Pass queryParams to API call ---
          response = await getAvailableCourses(queryParams);
        }

        console.log("Raw API Response:", JSON.stringify(response));

        if (response && response.code === 200) {
          const courses = response.data; // Assuming backend returns just the array now
          console.log("Extracted Courses:", JSON.stringify(courses));

          if (!Array.isArray(courses)) {
             console.error("API did not return an array for courses!");
             this.$message.error('获取课程数据格式错误');
             this.enrolledCourses = [];
             this.availableCourses = [];
             return;
          }

          if (this.activeTab === 'enrolled') {
            this.enrolledCourses = courses;
            console.log("Updated enrolledCourses:", this.enrolledCourses);
          } else {
            this.availableCourses = courses;
            console.log("Updated availableCourses:", this.availableCourses);
          }
        } else {
          this.$message.error(`获取课程列表失败: ${  response ? response.message : '未知错误'}`);
          this.enrolledCourses = [];
          this.availableCourses = [];
        }
      } catch (error) {
        console.error('获取课程列表失败:', error);
        this.$message.error(`获取课程列表失败: ${  error.message}`);
        this.enrolledCourses = [];
        this.availableCourses = [];
      } finally {
        this.loading = false;
      }
    },
    handleTabChange() {
      // Reset search when changing tabs? Optional.
      // this.searchQuery = '';
      this.fetchData()
    },
    handleFilter() { // This method now correctly triggers fetchData which uses searchQuery
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
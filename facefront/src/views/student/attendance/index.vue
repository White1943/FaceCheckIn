<template>
  <div class="student-attendance">
    <el-card>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="当前可签到" name="active">
          <el-table :data="activeTasks" v-loading="loading">
            <el-table-column label="课程" prop="courseName" />
            <el-table-column label="教师" prop="teacherName" />
            <el-table-column label="签到时间">
              <template #default="scope">
                {{ scope.row.startTime }} - {{ scope.row.endTime }}
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template #default="scope">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="handleAttendance(scope.row)"
                >
                  签到
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="签到记录" name="history">
          <el-table :data="historyRecords" v-loading="loading">
            <el-table-column label="课程" prop="courseName" />
            <el-table-column label="教师" prop="teacherName" />
            <el-table-column label="签到时间">
              <template #default="scope">
                {{ scope.row.startTime }} - {{ scope.row.endTime }}
              </template>
            </el-table-column>
            <el-table-column label="签到状态" prop="status">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="签到时间" prop="checkInTime" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { getActiveAttendanceTasks, getAttendanceHistory, submitAttendance } from '@/api/attendance'

export default {
  name: 'StudentAttendance',
  data() {
    return {
      activeTab: 'active',
      activeTasks: [],
      historyRecords: [],
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
        if (this.activeTab === 'active') {
          const response = await getActiveAttendanceTasks()
          if (response.code === 200) {
            this.activeTasks = response.data.items
          }
        } else {
          const response = await getAttendanceHistory()
          if (response.code === 200) {
            this.historyRecords = response.data.items
          }
        }
      } catch (error) {
        console.error('获取签到数据失败:', error)
        this.$message.error('获取签到数据失败')
      } finally {
        this.loading = false
      }
    },
    async handleAttendance(task) {
      try {
        // TODO: 获取位置信息和人脸图片
        const data = {
          taskId: task.taskId,
          locationLat: 0,  // 需要获取实际位置
          locationLng: 0,  // 需要获取实际位置
          faceImage: ''    // 需要获取人脸图片
        }
        
        const response = await submitAttendance(data)
        if (response.code === 200) {
          this.$message.success('签到成功')
          this.fetchData()
        }
      } catch (error) {
        console.error('签到失败:', error)
        this.$message.error('签到失败')
      }
    },
    getStatusType(status) {
      const statusMap = {
        '正常': 'success',
        '迟到': 'warning',
        '缺课': 'danger'
      }
      return statusMap[status] || 'info'
    }
  },
  watch: {
    activeTab() {
      this.fetchData()
    }
  }
}
</script>

<style lang="scss" scoped>
.student-attendance {
  padding: 20px;
}
</style> 
<template>
  <div class="task-details-view">
    <el-card>
      <div slot="header" class="card-header">
        <span>签到详情: {{ taskName }}</span>
        <el-button type="primary" icon="el-icon-refresh" @click="fetchDetails">刷新</el-button>
      </div>

      <el-table :data="studentList" v-loading="loading" style="width: 100%">
        <el-table-column label="学生姓名" prop="studentName" min-width="120" />
        <el-table-column label="签到状态" prop="status" min-width="100">
           <template slot-scope="scope">
             <el-tag :type="getStatusTagType(scope.row.status)">
               {{ scope.row.status }}
             </el-tag>
           </template>
        </el-table-column>
        <el-table-column label="签到时间" prop="checkInTime" min-width="160">
           <template slot-scope="scope">
             {{ scope.row.checkInTime || '-' }}
           </template>
        </el-table-column>
         <el-table-column label="签到照片" min-width="100" align="center">
           <template slot-scope="scope">
             <el-image
               v-if="scope.row.faceImageUrl"
               style="width: 40px; height: 40px; border-radius: 50%; cursor: pointer;"
               :src="getImageUrl(scope.row.faceImageUrl)"
               :preview-src-list="[getImageUrl(scope.row.faceImageUrl)]"
               fit="cover">
                <div slot="error" class="image-slot">
                  <i class="el-icon-picture-outline"></i>
                </div>
             </el-image>
             <span v-else>-</span>
           </template>
         </el-table-column>
      </el-table>
       <el-empty v-if="!loading && studentList.length === 0" description="暂无学生签到数据"></el-empty>
    </el-card>
  </div>
</template>

<script>
import { getTaskAttendanceDetails } from '@/api/attendance'
import { baseURL } from '@/config' // Import baseURL if needed for image paths

export default {
  name: 'TaskAttendanceDetails',
  props: {
    taskId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      loading: false,
      studentList: [],
      taskName: ''
    }
  },
  watch: {
    taskId: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.fetchDetails()
        }
      }
    }
  },
  methods: {
    async fetchDetails() {
      if (!this.taskId) return
      this.loading = true
      try {
        const response = await getTaskAttendanceDetails(this.taskId)
        if (response.code === 200) {
          this.studentList = response.data.items
          this.taskName = response.data.taskName || `任务 ${this.taskId}`
        } else {
          this.$message.error(response.message || '获取签到详情失败')
        }
      } catch (error) {
        console.error('获取签到详情失败:', error)
        this.$message.error('获取签到详情失败')
      } finally {
        this.loading = false
      }
    },
    getStatusTagType(status) {
      switch (status) {
        case '正常': return 'success'
        case '迟到': return 'warning'
        case '缺课': return 'danger'
        case '异常': return 'info'
        case '未签到': return 'primary'
        default: return 'info'
      }
    },
     // Helper to construct full image URL if needed
    getImageUrl(relativePath) {
      if (!relativePath) return null;
      // Assuming backend serves static files correctly and relativePath starts with /uploads/...
      // Adjust if your backend serves files differently (e.g., needs full base URL)
      // Example: return `${baseURL}${relativePath}` if baseURL is configured and needed
       return `http://localhost:5001${relativePath}`; // Hardcoding for now, adjust as needed
    }
  }
}
</script>

<style lang="scss" scoped>
.task-details-view {
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
    color: #909399;
    font-size: 20px;
  }
}
</style> 
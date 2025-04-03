<template>
  <div class="student-appeals">
    <el-card>
      <div slot="header">
        <span>签到申诉记录</span>
      </div>
      
      <el-table :data="appealsList" v-loading="loading">
        <el-table-column label="课程" prop="courseName" />
        <el-table-column label="签到时间" prop="checkInTime" />
        <el-table-column label="状态">
          <template slot-scope="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="申诉状态">
          <template slot-scope="scope">
            <el-tag :type="getReviewStatusType(scope.row.reviewStatus)">
              {{ scope.row.reviewStatus }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="申诉理由" prop="appealReason" show-overflow-tooltip />
      </el-table>
      
      <div class="empty-block" v-if="appealsList.length === 0 && !loading">
        <el-empty description="暂无申诉记录"></el-empty>
      </div>
    </el-card>
  </div>
</template>

<script>
import { getStudentAppeals } from '@/api/attendance';

export default {
  name: 'StudentAppeals',
  data() {
    return {
      loading: false,
      appealsList: []
    }
  },
  created() {
    this.fetchAppeals();
  },
  methods: {
    async fetchAppeals() {
      this.loading = true;
      try {
        const response = await getStudentAppeals();
        if (response.code === 200) {
          this.appealsList = response.data.items;
        } else {
          this.$message.error(response.message || '获取申诉记录失败');
        }
      } catch (error) {
        console.error('获取申诉记录失败:', error);
        this.$message.error('获取申诉记录失败');
      } finally {
        this.loading = false;
      }
    },
    
    getStatusType(status) {
      const map = {
        '正常': 'success',
        '迟到': 'warning',
        '缺课': 'danger',
        '异常': 'info'
      };
      return map[status] || 'info';
    },
    
    getReviewStatusType(status) {
      const map = {
        '待审核': 'warning',
        '已审核': 'success',
        '未申诉': 'info'
      };
      return map[status] || 'info';
    }
  }
}
</script>

<style lang="scss" scoped>
.student-appeals {
  padding: 20px;
  
  .empty-block {
    margin-top: 20px;
    text-align: center;
  }
}
</style> 
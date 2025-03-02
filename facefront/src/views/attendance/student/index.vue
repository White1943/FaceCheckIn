<template>
  <div class="attendance-student">
    <el-card>
      <!-- 当前可签到任务 -->
      <div class="active-tasks">
        <h3>当前可签到</h3>
        <el-table :data="activeTasks" style="width: 100%">
          <el-table-column label="课程" prop="courseName" />
          <el-table-column label="签到任务" prop="taskName" />
          <el-table-column label="教师" prop="teacherName" />
          <el-table-column label="截止时间" prop="endTime" />
          <el-table-column label="操作">
            <template slot-scope="scope">
              <el-button size="small" type="primary" @click="doCheckIn(scope.row)">签到</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 历史签到记录 -->
      <div class="history-records" style="margin-top: 20px">
        <h3>签到记录</h3>
        <el-table :data="historyRecords" style="width: 100%">
          <el-table-column label="课程" prop="courseName" />
          <el-table-column label="签到任务" prop="taskName" />
          <el-table-column label="签到时间" prop="checkInTime" />
          <el-table-column label="状态" prop="status" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script>
  export default {
    name: 'AttendanceStudent',
    data() {
      return {
        activeTasks: [],
        historyRecords: [],
      }
    },
    methods: {
      // 实现相关方法
    },
  }
</script>

<style scoped>
  .attendance-student {
    padding: 20px;
  }
</style>

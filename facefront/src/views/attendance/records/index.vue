<template>
  <div class="attendance-records">
    <h1>签到记录</h1>
    <el-table :data="records" style="width: 100%">
      <el-table-column label="学生姓名" prop="studentName" />
      <el-table-column label="签到日期" prop="attendanceDate" />
      <el-table-column label="状态" prop="status" />
    </el-table>
  </div>
</template>

<script>
  export default {
    name: 'AttendanceRecords',
    data() {
      return {
        records: [
          { studentName: '张三', attendanceDate: '2023-02-21', status: '已签到' },
          { studentName: '李四', attendanceDate: '2023-02-21', status: '缺席' },
        ],
      }
    },
  }
</script>

<style scoped>
  .attendance-records {
    padding: 20px;
  }
</style>

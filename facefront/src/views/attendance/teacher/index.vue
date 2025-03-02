<template>
  <div class="attendance-teacher">
    <el-card>
      <div class="task-management">
        <el-button type="primary" @click="createTask">发起签到</el-button>

        <el-table :data="taskList" style="width: 100%; margin-top: 20px">
          <el-table-column label="签到任务" prop="taskName" />
          <el-table-column label="课程" prop="courseName" />
          <el-table-column label="开始时间" prop="startTime" />
          <el-table-column label="结束时间" prop="endTime" />
          <el-table-column label="状态" prop="status" />
          <el-table-column label="操作">
            <template #default="scope">
              <el-button type="text" @click="viewDetails(scope.row)">查看详情</el-button>
              <el-button v-if="scope.row.status === 'active'" type="text" @click="endTask(scope.row)">结束签到</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <el-dialog title="发起签到" :visible.sync="dialogVisible">
      <el-form ref="taskForm" :model="taskForm" :rules="rules">
        <el-form-item label="课程" prop="courseId">
          <el-select v-model="taskForm.courseId" placeholder="请选择课程">
            <el-option v-for="course in courseList" :key="course.id" :label="course.name" :value="course.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="签到名称" prop="taskName">
          <el-input v-model="taskForm.taskName" />
        </el-form-item>

        <el-form-item label="签到时间" prop="timeRange">
          <el-date-picker
            v-model="taskForm.timeRange"
            end-placeholder="结束时间"
            range-separator="至"
            start-placeholder="开始时间"
            type="datetimerange"
          />
        </el-form-item>

        <el-form-item label="签到说明" prop="description">
          <el-input v-model="taskForm.description" type="textarea" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTask">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
  export default {
    name: 'AttendanceTeacher',
    data() {
      return {
        taskList: [],
        courseList: [],
        dialogVisible: false,
        taskForm: {
          courseId: '',
          taskName: '',
          timeRange: [],
          description: '',
        },
        rules: {
          courseId: [{ required: true, message: '请选择课程', trigger: 'change' }],
          taskName: [{ required: true, message: '请输入签到名称', trigger: 'blur' }],
          timeRange: [{ required: true, message: '请选择时间范围', trigger: 'change' }],
        },
      }
    },
    methods: {
      // 实现相关方法
    },
  }
</script>

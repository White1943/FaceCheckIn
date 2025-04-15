<template>
  <div class="teacher-attendance">
    <el-card>
      <div class="filter-container">
        <el-select 
          v-model="selectedCourse" 
          placeholder="选择课程" 
          style="width: 200px; margin-right: 10px"
          @change="handleCourseChange"
        >
          <el-option
            v-for="course in courseList"
            :key="course.courseId"
            :label="course.courseName"
            :value="course.courseId"
          />
        </el-select>
        <el-button type="primary" @click="startAttendance">发起签到</el-button>
      </div>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="进行中的签到" name="active">
          <el-table :data="activeAttendanceList" v-loading="loading">
            <el-table-column label="课程" prop="courseName" />
            <el-table-column label="开始时间" prop="startTime" />
            <el-table-column label="结束时间" prop="endTime" />
            <el-table-column label="已签到/总人数" prop="attendanceRate" />
            <el-table-column label="操作">
              <template #default="scope">
                <el-button type="text" @click="endAttendance(scope.row)">
                  结束签到
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="历史记录" name="history">
          <el-table :data="historyAttendanceList" v-loading="loading">
            <el-table-column label="课程" prop="courseName" />
            <el-table-column label="日期" prop="date" />
            <el-table-column label="时间">
              <template #default="scope">
                {{ scope.row.startTime }} - {{ scope.row.endTime }}
              </template>
            </el-table-column>
            <el-table-column label="出勤率" prop="attendanceRate" />
            <el-table-column label="操作">
              <template #default="scope">
                <el-button type="text" @click="viewDetails(scope.row)">
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 发起签到对话框 -->
    <el-dialog title="发起签到" :visible.sync="dialogVisible" width="500px">
      <el-form ref="taskForm" :model="taskForm" :rules="rules" label-width="100px">
        <el-form-item label="课程" prop="courseId">
          <el-select v-model="taskForm.courseId" placeholder="请选择课程">
            <el-option
              v-for="course in courseList"
              :key="course.courseId"
              :label="course.courseName"
              :value="course.courseId"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="签到时间" prop="timeRange">
          <el-time-picker
            v-model="taskForm.timeRange[0]"
            format="HH:mm"
            placeholder="开始时间"
            style="width: 180px"
          />
          <span style="margin: 0 10px">至</span>
          <el-time-picker
            v-model="taskForm.timeRange[1]"
            format="HH:mm"
            placeholder="结束时间"
            style="width: 180px"
          />
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTask">确定</el-button>
      </div>
    </el-dialog>

    <!-- 签到详情对话框 -->
    <el-dialog title="签到详情" :visible.sync="detailsVisible" width="600px">
      <div v-if="currentTaskDetails">
        <div class="task-info">
          <p>课程：{{ currentTaskDetails.taskInfo.courseName }}</p>
          <p>时间：{{ currentTaskDetails.taskInfo.startTime }} 至 {{ currentTaskDetails.taskInfo.endTime }}</p>
        </div>
        <el-table :data="currentTaskDetails.records">
          <el-table-column label="学号" prop="studentId" />
          <el-table-column label="姓名" prop="studentName" />
          <el-table-column label="签到时间" prop="checkInTime" />
          <el-table-column label="状态" prop="status">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template #default="scope">
              <el-button 
                type="text" 
                @click="viewStudentPhoto(scope.row)"
                :disabled="!scope.row.faceImage"
              >
                查看照片
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 查看照片对话框 -->
    <el-dialog title="签到照片" :visible.sync="photoVisible" width="500px">
      <div class="photo-container" v-if="currentPhoto">
        <img :src="currentPhoto" alt="签到照片" style="width: 100%;">
      </div>
      <div v-else class="no-photo">
        <el-empty description="无签到照片"></el-empty>
      </div>
    </el-dialog>

    <!-- 过期任务自动结束提示 -->
    <el-alert
      v-if="autoEndedTasksCount > 0"
      title="系统消息"
      type="info"
      :description="`系统已自动结束 ${autoEndedTasksCount} 个过期的签到任务`"
      show-icon
      :closable="true"
      @close="clearAutoEndedNotification"
      style="margin-bottom: 15px;"
    />
  </div>
</template>

<script>
import { getTeacherCourses, createAttendanceTask, getAttendanceTasks, endAttendanceTask, getTaskRecords  } from '@/api/attendance'

export default {
  name: 'TeacherAttendance',
  data() {
    return {
      selectedCourse: '',  // 当前选中的课程ID
      courseList: [],      // 课程列表
      activeTab: 'active', // 当前激活的标签页
      activeAttendanceList: [], // 进行中的签到列表
      historyAttendanceList: [],
      loading: false,      // 加载状态
      dialogVisible: false, // 对话框显示状态
      taskForm: {          // 签到任务表单
        courseId: '',
        timeRange: []
      },
      rules: {
        courseId: [{ required: true, message: '请选择课程', trigger: 'change' }],
        timeRange: [{ required: true, message: '请选择时间范围', trigger: 'change' }]
      },
      detailsVisible: false,
      currentTaskDetails: null,
      photoVisible: false,   // 照片查看对话框显示状态
      currentPhoto: null,    // 当前查看的照片URL
      apiBaseUrl: 'http://localhost:5001',  // 后端API基础URL
      // 新增自动结束任务计数
      autoEndedTasksCount: 0
    }
  },
  created() {
    this.fetchCourses()
    this.fetchAttendanceTasks()
  },
  methods: {
    // 获取教师的课程列表
    async fetchCourses() {
      try {
        const response = await getTeacherCourses()
        if (response.code === 200) {
          this.courseList = response.data.items
        }
      } catch (error) {
        console.error('获取课程列表失败:', error)
        this.$message.error('获取课程列表失败')
      }
    },
    // 获取签到任务列表
    async fetchAttendanceTasks() {
      try {
        this.loading = true
        const params = {
          courseId: this.selectedCourse || undefined,
          type: this.activeTab
        }
        const response = await getAttendanceTasks(params)
        if (response.code === 200) {
          if (this.activeTab === 'active') {
            this.activeAttendanceList = response.data.items
          } else {
            this.historyAttendanceList = response.data.items
          }
          
          // 检查是否有任务被自动结束
          if (response.data.autoEndedCount && response.data.autoEndedCount > 0) {
            this.autoEndedTasksCount = response.data.autoEndedCount
          }
        }
      } catch (error) {
        console.error('获取签到任务列表失败:', error)
        this.$message.error('获取签到任务列表失败')
      } finally {
        this.loading = false
      }
    },
    // 处理课程选择变化
    handleCourseChange() {
      this.fetchAttendanceTasks()
    },
    // 打开发起签到对话框
    startAttendance() {
      this.dialogVisible = true
      this.taskForm = {
        courseId: this.selectedCourse || '',
        timeRange: []
      }
    },
    // 提交签到任务
    async submitTask() {
      try {
        await this.$refs.taskForm.validate()
        const [startTime, endTime] = this.taskForm.timeRange
        
        // 格式化时间
        const formatTime = (date) => {
          const hours = date.getHours().toString().padStart(2, '0')
          const minutes = date.getMinutes().toString().padStart(2, '0')
          return `${hours}:${minutes}`
        }

        const data = {
          courseId: this.taskForm.courseId,
          startTime: formatTime(startTime),
          endTime: formatTime(endTime)
        }

        const response = await createAttendanceTask(data)
        if (response.code === 200) {
          this.$message.success('签到任务创建成功')
          this.dialogVisible = false
          this.fetchAttendanceTasks()
        }
      } catch (error) {
        console.error('创建签到任务失败:', error)
        this.$message.error('创建签到任务失败')
      }
    },
    // 结束签到任务
    async endAttendance(task) {
      try {
        await this.$confirm('确认结束该签到任务?', '提示', {
          type: 'warning'
        })
        const response = await endAttendanceTask(task.taskId)
        if (response.code === 200) {
          this.$message.success('签到任务已结束')
          this.fetchAttendanceTasks()
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('结束签到任务失败:', error)
          this.$message.error('结束签到任务失败')
        }
      }
    },
    // 查看学生签到照片
    async viewStudentPhoto(record) {
      if (!record.faceImage) {
        this.$message.warning('该学生没有上传签到照片');
        return;
      }
      
      try {
        // 完整URL构建
        const imageUrl = `http://localhost:5001${record.faceImage}`;
        console.log('加载照片URL:', imageUrl); // 调试输出
        this.currentPhoto = imageUrl;
        this.photoVisible = true;
      } catch (error) {
        this.$message.error('获取照片失败');
        console.error(error);
      }
    },
    // 查看签到详情
    async viewDetails(task) {
      try {
        const response = await getTaskRecords(task.taskId)
        if (response.code === 200) {
          this.currentTaskDetails = response.data
          this.detailsVisible = true
        }
      } catch (error) {
        console.error('获取签到详情失败:', error)
        this.$message.error('获取签到详情失败')
      }
    },
    getStatusType(status) {
      const statusMap = {
        '正常': 'success',
        '迟到': 'warning',
        '缺课': 'danger'
      }
      return statusMap[status] || 'info'
    },
    // 清除自动结束任务的通知
    clearAutoEndedNotification() {
      this.autoEndedTasksCount = 0
    }
  },
  watch: {
    activeTab() {
      this.fetchAttendanceTasks()
    }
  }
}
</script>

<style lang="scss" scoped>
.teacher-attendance {
  padding: 20px;

  .filter-container {
    margin-bottom: 20px;
  }
}

.face-photo {
  width: 100%;
  max-height: 400px;
  object-fit: contain;
}

.photo-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.no-photo {
  text-align: center;
  padding: 20px;
  color: #909399;
}
</style> 
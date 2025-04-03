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
                  @click="openFaceRecognition(scope.row)"
                >
                  人脸签到
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

    <!-- 人脸识别摄像头弹窗 -->
    <el-dialog 
      title="人脸识别签到" 
      :visible.sync="cameraDialogVisible" 
      width="600px"
      :close-on-click-modal="false"
      :close-on-press-escape="false">
      <div class="camera-container">
        <div v-if="!capturedImage">
          <video 
            ref="video" 
            width="100%" 
            height="375" 
            autoplay 
            class="camera-video">
          </video>
          <div class="camera-hint">
            请确保光线充足，面部正对摄像头
          </div>
          <div class="camera-controls">
            <el-button type="primary" @click="captureImage">拍照</el-button>
          </div>
        </div>
        
        <div v-else class="preview-container">
          <img :src="capturedImage" alt="预览" class="preview-image">
          <div class="preview-controls">
            <el-button type="primary" @click="submitAttendance">确认提交</el-button>
            <el-button @click="retakePhoto">重新拍照</el-button>
          </div>
        </div>
      </div>
      
      <div v-if="recognizing" class="recognizing-overlay">
        <div class="recognizing-spinner">
          <i class="el-icon-loading"></i>
          <p>正在进行人脸识别...</p>
        </div>
      </div>
    </el-dialog>

    
    <!-- 申诉对话框 -->
    <el-dialog 
      title="提交签到申诉" 
      :visible.sync="appealDialogVisible" 
      width="500px">
      <el-form :model="appealForm" ref="appealForm" :rules="appealRules" label-width="80px">
        <el-form-item label="申诉理由" prop="reason">
          <el-input 
            type="textarea" 
            v-model="appealForm.reason" 
            :rows="6"
            placeholder="请详细说明签到异常的原因，如光线不足、网络问题等"
          ></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="appealDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAppeal">提交申诉</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getActiveAttendanceTasks, getAttendanceHistory, submitAttendance, submitAppeal } from '@/api/attendance'
import axios from 'axios'
import { getAccessToken } from '@/utils/accessToken'

export default {
  name: 'StudentAttendance',
  data() {
    return {
      activeTab: 'active',
      activeTasks: [],
      historyRecords: [],
      loading: false,
      cameraDialogVisible: false,
      stream: null,
      capturedImage: null,
      selectedTask: null,
      recognizing: false,
      appealDialogVisible: false,
      appealForm: {
        recordId: null,
        reason: ''
      },
      appealRules: {
        reason: [
          { required: true, message: '请输入申诉理由', trigger: 'blur' },
          { min: 10, message: '申诉理由至少10个字符', trigger: 'blur' }
        ]
      }
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
    getStatusType(status) {
      const statusMap = {
        '正常': 'success',
        '迟到': 'warning',
        '缺课': 'danger'
      }
      return statusMap[status] || 'info'
    },
    
    // 打开人脸识别对话框
    openFaceRecognition(task) {
      this.selectedTask = task;
      this.cameraDialogVisible = true;
      this.capturedImage = null;
      
      // 启动摄像头
      this.$nextTick(() => {
        this.startCamera();
      });
    },
    
    // 启动摄像头
    async startCamera() {
      try {
        if (this.stream) {
          // 关闭已存在的流
          this.stopCamera();
        }
        
        // 获取新的流
        this.stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user' },
          audio: false
        });
        
        // 确保视频元素存在后再设置
        if (this.$refs.video) {
          this.$refs.video.srcObject = this.stream;
        }
      } catch (error) {
        console.error('无法访问摄像头:', error);
        this.$message.error('无法访问摄像头，请检查摄像头权限');
      }
    },
    
    // 停止摄像头
    stopCamera() {
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop());
        this.stream = null;
      }
    },
    
    // 拍照
    captureImage() {
      const video = this.$refs.video;
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const context = canvas.getContext('2d');
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // 将图像转换为base64
      this.capturedImage = canvas.toDataURL('image/jpeg');
      
      // 将base64转换为Blob以便上传
      canvas.toBlob(blob => {
        this.imageBlob = blob;
      }, 'image/jpeg', 0.95);
    },
    
    // 重新拍照
    retakePhoto() {
      this.capturedImage = null;
      // 关键修复：确保在显示摄像头前已经获取到视频流
      this.$nextTick(() => {
        // 如果流已关闭，重新获取
        if (!this.stream || this.stream.active === false) {
          this.startCamera();
        } else {
          // 确保视频元素正确绑定到现有流
          this.$refs.video.srcObject = this.stream;
        }
      });
    },
    
    // 提交签到
    async submitAttendance() {
      this.recognizing = true;
      try {
        console.log('任务ID:', this.selectedTask.taskId);
        
        // 创建一个新的FormData对象
        const formData = new FormData();
        
        // 添加数据到FormData
        formData.append('task_id', this.selectedTask.taskId);
        // 只有当位置信息可用时才添加
        if (this.currentLocation && this.currentLocation.latitude) {
          formData.append('location_lat', this.currentLocation.latitude);
          formData.append('location_lng', this.currentLocation.longitude);
        }
        
        // 添加图像
        if (this.imageBlob) {
          formData.append('face_image', this.imageBlob, 'face.jpg');
        } else {
          this.$message.error('未能获取照片');
          this.recognizing = false;
          return;
        }
        
        // 打印调试信息 - 不要直接打印FormData对象，而是打印每个字段
        console.log('表单数据:');
        for (let [key, value] of formData.entries()) {
          console.log(`${key}: ${value instanceof Blob ? 'Blob数据' : value}`);
        }
        
        // 尝试直接使用axios发送请求，跳过封装的API
        const response = await axios({
          method: 'post',
          url: 'http://localhost:5001/api/stu/attendance/sign',
          data: formData,
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${getAccessToken()}`
          }
        });
        
        // 处理响应
        if (response.data.code === 200) {
          this.$message.success(response.data.message || '签到成功');
          this.cameraDialogVisible = false;
          
          // 如果是异常签到，询问是否申诉
          if (response.data.data && response.data.data.status === '异常') {
            this.handleAbnormalSign(response.data.data.recordId);
          }
          
          // 刷新签到记录
          this.fetchData();
        } else {
          this.$message.error(response.data.message || '签到失败');
        }
      } catch (error) {
        console.error('签到错误:', error);
        this.$message.error(`签到失败: ${  error.response?.data?.message || error.message || '未知错误'}`);
      } finally {
        this.recognizing = false;
      }
    },
    
    // 获取当前位置
    getCurrentPosition() {
      return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
          reject(new Error('浏览器不支持地理位置'));
          return;
        }
        
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 5000,
          maximumAge: 0
        });
      });
    },
    
    // 将base64转换为Blob
    dataURItoBlob(dataURI) {
      const byteString = atob(dataURI.split(',')[1]);
      const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
      const ia = new Uint8Array(byteString.length);
      for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
      }
      return new Blob([ia], { type: mimeString });
    },
    
    // 处理异常签到结果
    handleAbnormalSign(recordId) {
      this.$confirm('您的签到已记录为异常，是否提交申诉?', '签到异常', {
        confirmButtonText: '提交申诉',
        cancelButtonText: '稍后处理',
        type: 'warning'
      }).then(() => {
        this.openAppealDialog(recordId);
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '您可以稍后在"签到记录"中提交申诉'
        });
      });
    },
    
    // 打开申诉对话框
    openAppealDialog(recordId) {
      this.appealForm.recordId = recordId;
      this.appealForm.reason = '';
      this.appealDialogVisible = true;
    },
    
    // 提交申诉
    async submitAppeal() {
      this.$refs.appealForm.validate(async (valid) => {
        if (valid) {
          try {
            const response = await submitAppeal(this.appealForm);
            
            if (response.code === 200) {
              this.$message.success('申诉提交成功');
              this.appealDialogVisible = false;
              // 刷新签到记录
              this.fetchData();
            }
          } catch (error) {
            console.error('提交申诉失败:', error);
            this.$message.error('申诉提交失败');
          }
        }
      });
    }
  },
  watch: {
    activeTab() {
      this.fetchData();
    },
    cameraDialogVisible(val) {
      if (!val) {
        this.stopCamera();
      }
    }
  },
  beforeDestroy() {
    this.stopCamera();
  }
}
</script>

<style lang="scss" scoped>
.student-attendance {
  padding: 20px;
}

.camera-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.camera-video {
  border-radius: 8px;
  background-color: #000;
  max-width: 100%;
}

.camera-hint {
  color: #606266;
  font-size: 14px;
  margin: 15px 0;
  text-align: center;
}

.camera-controls {
  margin-top: 15px;
  display: flex;
  justify-content: center;
}

.preview-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.preview-image {
  max-width: 100%;
  border-radius: 8px;
}

.preview-controls {
  margin-top: 15px;
  display: flex;
  justify-content: center;
  gap: 15px;
}

.recognizing-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.recognizing-spinner {
  text-align: center;
}

.recognizing-spinner i {
  font-size: 32px;
  color: #409EFF;
}

.recognizing-spinner p {
  margin-top: 10px;
  color: #606266;
}
</style> 
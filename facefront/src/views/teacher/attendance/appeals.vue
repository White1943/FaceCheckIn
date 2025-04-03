<template>
  <div class="appeals-review">
    <el-card>
      <div slot="header">
        <span>签到申诉审核</span>
      </div>
      
      <el-table :data="appealsList" v-loading="loading">
        <el-table-column label="学生" prop="studentName" />
        <el-table-column label="课程" prop="courseName" />
        <el-table-column label="签到时间" prop="checkInTime" />
        <el-table-column label="申诉理由" prop="appealReason" show-overflow-tooltip />
        <el-table-column label="操作" width="200">
          <template slot-scope="scope">
            <el-button 
              type="text" 
              @click="viewPhoto(scope.row)"
              :disabled="!scope.row.faceImage"
            >
              查看照片
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="handleApprove(scope.row)"
            >
              通过
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleReject(scope.row)"
            >
              拒绝
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="empty-block" v-if="appealsList.length === 0 && !loading">
        <el-empty description="暂无待审核的申诉"></el-empty>
      </div>
    </el-card>
    
    <!-- 照片查看对话框 -->
    <el-dialog title="签到照片" :visible.sync="photoDialogVisible" width="500px">
      <div class="photo-container" v-if="currentPhoto">
        <img :src="currentPhoto" alt="签到照片" style="width: 100%;" />
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getAppeals, reviewAppeal } from '@/api/attendance';

export default {
  name: 'AppealsReview',
  data() {
    return {
      appealsList: [],
      loading: false,
      photoDialogVisible: false,
      currentPhoto: null
    }
  },
  created() {
    this.fetchAppeals();
  },
  methods: {
    async fetchAppeals() {
      this.loading = true;
      try {
        const response = await getAppeals();
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
    
    viewPhoto(record) {
      if (record.faceImage) {
        this.currentPhoto = `http://localhost:5001${record.faceImage}`;
        this.photoDialogVisible = true;
      } else {
        this.$message.warning('无签到照片');
      }
    },
    
    async handleApprove(record) {
      try {
        await this.$confirm('确认通过此申诉？通过后学生签到将被标记为正常', '提示', {
          type: 'warning'
        });
        
        const response = await reviewAppeal(record.recordId, { approved: true });
        if (response.code === 200) {
          this.$message.success('已通过申诉');
          this.fetchAppeals();
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('审核申诉失败:', error);
          this.$message.error('操作失败');
        }
      }
    },
    
    async handleReject(record) {
      try {
        await this.$confirm('确认拒绝此申诉？拒绝后签到状态将保持异常', '提示', {
          type: 'warning'
        });
        
        const response = await reviewAppeal(record.recordId, { approved: false });
        if (response.code === 200) {
          this.$message.success('已拒绝申诉');
          this.fetchAppeals();
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('审核申诉失败:', error);
          this.$message.error('操作失败');
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.appeals-review {
  padding: 20px;
  
  .empty-block {
    margin-top: 20px;
    text-align: center;
  }
  
  .photo-container {
    display: flex;
    justify-content: center;
    
    img {
      max-width: 100%;
      border-radius: 4px;
    }
  }
}
</style> 
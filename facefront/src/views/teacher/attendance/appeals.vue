<template>
  <div class="appeals-review">
    <el-card>
      <div slot="header" class="card-header">
        <span class="header-title">签到申诉审核</span>
        <el-button type="primary" size="small" icon="el-icon-refresh" @click="fetchAppeals">刷新</el-button>
      </div>
      
      <el-table 
        v-loading="loading" 
        :data="appealsList" 
        border 
        style="width: 100%"
        :header-cell-style="{background:'#f5f7fa', color:'#606266'}">
        <el-table-column label="学生" prop="studentName" min-width="100" />
        <el-table-column label="课程" prop="courseName" min-width="160" />
        <el-table-column label="签到时间" prop="checkInTime" min-width="160" />
        <el-table-column label="申诉理由" prop="appealReason" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" min-width="200" align="center">
          <template slot-scope="scope">
            <div class="operation-buttons">
              <el-button 
                type="primary" 
                plain
                size="small" 
                icon="el-icon-picture"
                :disabled="!scope.row.faceImage"
                @click="viewPhoto(scope.row)">
                查看照片
              </el-button>
              <div class="approval-buttons">
                <el-button 
                  type="success" 
                  size="small" 
                  icon="el-icon-check"
                  @click="handleApprove(scope.row)">
                  通过
                </el-button>
                <el-button 
                  type="danger" 
                  size="small" 
                  icon="el-icon-close"
                  @click="handleReject(scope.row)">
                  拒绝
                </el-button>
              </div>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-if="appealsList.length === 0 && !loading" class="empty-block">
        <el-empty description="暂无待审核的申诉">
          <el-button type="primary" @click="fetchAppeals">刷新</el-button>
        </el-empty>
      </div>
      
      <el-pagination
        v-if="appealsList.length > 0"
        :current-page="currentPage"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalCount || appealsList.length"
        class="pagination"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange">
      </el-pagination>
    </el-card>
    
    <!-- 照片查看对话框 -->
    <el-dialog 
      title="签到照片" 
      :visible.sync="photoDialogVisible" 
      width="500px"
      custom-class="photo-dialog">
      <div v-if="currentPhoto" class="photo-container">
        <img :src="currentPhoto" alt="签到照片" class="appeal-photo" />
      </div>
      <div v-if="currentRecord" class="photo-info">
        <p><strong>学生：</strong>{{ currentRecord.studentName }}</p>
        <p><strong>签到时间：</strong>{{ currentRecord.checkInTime }}</p>
        <p><strong>申诉理由：</strong>{{ currentRecord.appealReason }}</p>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="photoDialogVisible = false">关闭</el-button>
        <el-button type="success" @click="handleApprove(currentRecord)">通过申诉</el-button>
        <el-button type="danger" @click="handleReject(currentRecord)">拒绝申诉</el-button>
      </span>
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
      currentPhoto: null,
      currentRecord: null,
      currentPage: 1,
      pageSize: 10,
      totalCount: 0
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
          this.totalCount = this.appealsList.length;
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
        this.currentRecord = record;
        this.photoDialogVisible = true;
      } else {
        this.$message.warning('无签到照片');
      }
    },
    
    async handleApprove(record) {
      if (!record) return;
      
      try {
        await this.$confirm('确认通过此申诉？通过后学生签到将被标记为正常', '提示', {
          type: 'warning'
        });
        
        const response = await reviewAppeal(record.recordId, { approved: true });
        if (response.code === 200) {
          this.$message.success('已通过申诉');
          this.photoDialogVisible = false;
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
      if (!record) return;
      
      try {
        await this.$confirm('确认拒绝此申诉？拒绝后签到状态将保持异常', '提示', {
          type: 'warning'
        });
        
        const response = await reviewAppeal(record.recordId, { approved: false });
        if (response.code === 200) {
          this.$message.success('已拒绝申诉');
          this.photoDialogVisible = false;
          this.fetchAppeals();
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('审核申诉失败:', error);
          this.$message.error('操作失败');
        }
      }
    },
    
    handleSizeChange(val) {
      this.pageSize = val;
    },
    
    handleCurrentChange(val) {
      this.currentPage = val;
    }
  }
}
</script>

<style lang="scss" scoped>
.appeals-review {
  padding: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .header-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }
  
  .operation-buttons {
    display: flex;
    flex-direction: column;
    gap: 8px;
    
    .approval-buttons {
      display: flex;
      justify-content: center;
      gap: 8px;
    }
  }
  
  .empty-block {
    margin: 30px 0;
    text-align: center;
  }
  
  .pagination {
    margin-top: 20px;
    text-align: right;
  }
}

.photo-dialog {
  .photo-container {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
    
    .appeal-photo {
      max-width: 100%;
      max-height: 400px;
      border-radius: 4px;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    }
  }
  
  .photo-info {
    padding: 15px;
    margin-bottom: 10px;
    background-color: #f9f9f9;
    border-radius: 4px;
    
    p {
      margin: 8px 0;
      line-height: 1.5;
    }
  }
}
</style> 
 
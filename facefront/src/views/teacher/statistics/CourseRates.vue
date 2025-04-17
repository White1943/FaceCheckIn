<template>
  <div class="course-rates-statistics">
    <el-card>
      <div slot="header" class="card-header">
        <span>课程签到率统计</span>
        <div>
          <el-select
            v-model="selectedCourseId"
            placeholder="筛选课程"
            clearable
            @change="fetchRates"
            style="margin-right: 10px;"
          >
            <el-option
              v-for="course in teacherCourses"
              :key="course.courseId"
              :label="course.courseName"
              :value="course.courseId"
            />
          </el-select>
          <el-button
            type="success"
            icon="el-icon-download"
            @click="handleExport"
            :disabled="loading || chartData.length === 0"
            style="margin-left: 10px;"
          >
            导出数据
          </el-button>
          <el-button type="primary" icon="el-icon-refresh" @click="fetchRates">刷新</el-button>
        </div>
      </div>

      <div v-loading="loading" style="height: 400px;">
        <div ref="chart" style="width: 100%; height: 100%;"></div>
        <el-empty v-if="!loading && chartData.length === 0" description="暂无签到任务数据"></el-empty>
      </div>

      <!-- Optional: Display data in a table as well -->
       <el-table :data="chartData" style="width: 100%; margin-top: 20px;" v-if="chartData.length > 0">
         <el-table-column prop="courseName" label="课程名称" />
         <el-table-column prop="date" label="任务时间" />
         <el-table-column prop="attendanceRate" label="签到率 (%)" />
         <el-table-column prop="checkedInCount" label="已签人数" />
         <el-table-column prop="totalStudents" label="应签人数" />
       </el-table>

    </el-card>
  </div>
</template>

<script>
import { getCourseAttendanceRates, getTaskAttendanceDetails } from '@/api/attendance'
import { getTeacherCourses } from '@/api/course' // Assuming you have this API
import * as echarts from 'echarts'
import * as XLSX from 'xlsx'

export default {
  name: 'CourseRatesStatistics',
  data() {
    return {
      loading: false,
      exportLoading: false,
      chartData: [],
      teacherCourses: [],
      selectedCourseId: null,
      chartInstance: null,
      xAxisLabels: []
    }
  },
  async created() {
    await this.fetchTeacherCourses()
    await this.fetchRates()
  },
  mounted() {
    window.addEventListener('resize', this.resizeChart)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.resizeChart)
    if (this.chartInstance) {
      this.chartInstance.dispose()
    }
  },
  methods: {
    async fetchTeacherCourses() {
      try {
        const response = await getTeacherCourses() // Fetch courses for the filter dropdown
        if (response.code === 200) {
          this.teacherCourses = response.data.items
        }
      } catch (error) {
        console.error('获取教师课程列表失败:', error)
      }
    },
    async fetchRates() {
      this.loading = true
      try {
        const params = {}
        if (this.selectedCourseId) {
          params.courseId = this.selectedCourseId
        }
        const response = await getCourseAttendanceRates(params)
        if (response.code === 200) {
          this.chartData = response.data.items.reverse() || []
          this.updateChart()
        } else {
          this.chartData = []
          this.xAxisLabels = []
          if (this.chartInstance) {
             this.chartInstance.clear()
          }
          this.$message.error(response.message || '获取签到率数据失败')
        }
      } catch (error) {
        console.error('获取签到率数据失败:', error)
        this.chartData = []
        this.xAxisLabels = []
        if (this.chartInstance) {
           this.chartInstance.clear()
        }
        this.$message.error('获取签到率数据失败')
      } finally {
        this.loading = false
        if (!this.chartInstance && this.$refs.chart) {
            this.initChart()
        } else if (this.chartInstance) {
            this.updateChart()
        }
      }
    },
    initChart() {
      if (this.$refs.chart && !this.chartInstance) {
        this.chartInstance = echarts.init(this.$refs.chart)
      }
    },
    updateChart() {
      if (!this.chartInstance) {
         if (this.$refs.chart) {
             this.initChart()
             if (!this.chartInstance) return
         } else {
             console.warn("Chart DOM element not ready for update.")
             return
         }
      }

      this.xAxisLabels = this.chartData.map(item => `${item.date}\n${item.courseName}`)

      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const data = params[0].data;
            return `
              ${data.courseName}<br/>
              时间: ${data.date}<br/>
              签到率: ${data.attendanceRate}%<br/>
              人数: ${data.checkedInCount} / ${data.totalStudents}
            `;
          }
        },
        xAxis: {
          type: 'category',
          data: this.xAxisLabels,
          axisLabel: {
             interval: 0,
             rotate: 15
          }
        },
        yAxis: {
          type: 'value',
          name: '签到率 (%)',
          min: 0,
          max: 100,
          axisLabel: {
            formatter: '{value}%'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          containLabel: true
        },
        series: [
          {
            name: '签到率',
            type: 'bar',
            barWidth: '60%',
            data: this.chartData.map(item => ({
                value: item.attendanceRate,
                courseName: item.courseName,
                date: item.date,
                checkedInCount: item.checkedInCount,
                totalStudents: item.totalStudents
            })),
            itemStyle: {
              color: '#409EFF'
            },
            label: {
              show: true,
              position: 'top',
              formatter: '{c}%'
            }
          }
        ],
        dataZoom: [
          {
            type: 'slider',
            filterMode: 'filter',
            bottom: 10,
            height: 20,
            handleSize: '80%',
            showDetail: true,
            labelFormatter: (value) => {
                 if (this.xAxisLabels && this.xAxisLabels[value]) {
                     return this.xAxisLabels[value].split('\n')[0];
                 }
                 return '';
             }
          },
          {
            type: 'inside'
          }
        ],
      }
      this.chartInstance.setOption(option, true)
    },
    resizeChart() {
      if (this.chartInstance) {
        this.chartInstance.resize()
      }
    },
    async handleExport() {
      if (!this.chartInstance) {
          this.$message.error('图表未初始化，无法导出。');
          return;
      }

      const currentOptions = this.chartInstance.getOption();
      let startIndex = 0;
      let endIndex = this.chartData.length > 0 ? this.chartData.length - 1 : 0;

      if (currentOptions.dataZoom && currentOptions.dataZoom.length > 0) {
          const sliderZoom = currentOptions.dataZoom.find(dz => dz.type === 'slider');

          if (sliderZoom && typeof sliderZoom.startValue !== 'undefined' && typeof sliderZoom.endValue !== 'undefined') {
              startIndex = Math.max(0, Math.floor(sliderZoom.startValue));
              endIndex = Math.min(this.chartData.length - 1, Math.floor(sliderZoom.endValue));
              console.log('Read zoom directly from chart options:', startIndex, endIndex);
          } else {
               console.warn('Could not find valid start/end values in chart options dataZoom. Exporting full range.');
          }
      } else {
           console.warn('No dataZoom configuration found in chart options. Exporting full range.');
      }

      console.log('--- Export Triggered ---');
      console.log('Using startIndex:', startIndex);
      console.log('Using endIndex:', endIndex);
      console.log('Total chartData items:', this.chartData.length);
      if (this.xAxisLabels.length > 0 && startIndex >= 0 && endIndex < this.xAxisLabels.length && startIndex <= endIndex) {
          console.log('Label at startIndex:', this.xAxisLabels[startIndex]);
          console.log('Label at endIndex:', this.xAxisLabels[endIndex]);
      } else {
          console.warn('Cannot log labels due to invalid indices or empty labels array.');
      }

      if (startIndex < 0 || endIndex < 0 || startIndex > endIndex || startIndex >= this.chartData.length) {
          this.$message.warning('无法导出：无效的数据范围或无数据。');
          console.error("Invalid indices for export:", startIndex, endIndex, this.chartData.length);
          return;
      }

      const dataInView = this.chartData.slice(startIndex, endIndex + 1);

      console.log(`Sliced dataInView contains ${dataInView.length} items.`);
      if (dataInView.length > 0) {
          console.log('First item in view:', dataInView[0]?.date, dataInView[0]?.courseName);
          console.log('Last item in view:', dataInView[dataInView.length - 1]?.date, dataInView[dataInView.length - 1]?.courseName);
      }

      if (dataInView.length === 0) {
        this.$message.warning('当前选定范围内没有数据可以导出');
        return;
      }
      if (this.exportLoading) {
        this.$message.info('正在导出，请稍候...');
        return;
      }

      this.exportLoading = true;
      this.$message.info('正在准备详细数据，请稍候...');

      try {
        const taskIds = dataInView.map(item => item.taskId).filter(id => id != null);
        console.log('Task IDs being fetched for details:', taskIds);

        if (taskIds.length === 0) {
            this.$message.error('无法导出详细数据：未找到有效的任务ID。');
            this.exportLoading = false;
            return;
        }

        const detailPromises = taskIds.map(id => getTaskAttendanceDetails(id));
        const detailResponses = await Promise.all(detailPromises);

        const checkedInData = [];
        const absentData = [];

        detailResponses.forEach((response, index) => {
          if (response.code === 200 && response.data && response.data.items) {
            const taskInfo = dataInView.find(item => item.taskId === taskIds[index]) || {};
            const courseName = taskInfo.courseName || '未知课程';
            const taskDate = taskInfo.date || '未知时间';

            response.data.items.forEach(student => {
              const commonData = {
                '课程名称': courseName,
                '任务时间': taskDate,
                '学生姓名': student.studentName,
                '用户名': student.username || '-',
              };

              const checkedInStatuses = ['正常', '迟到'];

              if (checkedInStatuses.includes(student.status)) {
                checkedInData.push({
                  ...commonData,
                  '签到时间': student.checkInTime || '-',
                  '签到状态': student.status,
                });
              } else {
                absentData.push({
                  ...commonData,
                  '状态': student.status || '未签到',
                });
              }
            });
          } else {
            console.warn(`未能获取任务ID ${taskIds[index]} 的详细数据: ${response.message}`);
          }
        });

        const ratesDataToExport = dataInView.map(item => ({
          '课程名称': item.courseName,
          '任务时间': item.date,
          '签到率 (%)': item.attendanceRate,
          '已签人数': item.checkedInCount,
          '应签人数': item.totalStudents
        }));
        const ratesWorksheet = XLSX.utils.json_to_sheet(ratesDataToExport);
        const checkedInWorksheet = XLSX.utils.json_to_sheet(checkedInData);
        const absentWorksheet = XLSX.utils.json_to_sheet(absentData);

        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, ratesWorksheet, '课程签到率');
        XLSX.utils.book_append_sheet(workbook, checkedInWorksheet, '已签到学生');
        XLSX.utils.book_append_sheet(workbook, absentWorksheet, '未签到学生');

        const startDateStr = this.xAxisLabels[startIndex]?.split('\n')[0] || '未知开始日期';
        const endDateStr = this.xAxisLabels[endIndex]?.split('\n')[0] || '未知结束日期';
        const sanitizedStartDate = startDateStr.replace(/[:\s]/g, '_');
        const sanitizedEndDate = endDateStr.replace(/[:\s]/g, '_');

        const courseNamePart = this.selectedCourseId ? this.teacherCourses.find(c=>c.courseId === this.selectedCourseId)?.courseName || this.selectedCourseId : '所有课程';
        const fileName = `课程签到统计_${courseNamePart}_${sanitizedStartDate}_至_${sanitizedEndDate}.xlsx`;
        console.log('Generated filename:', fileName);

        XLSX.writeFile(workbook, fileName);
        this.$message.success('数据导出成功！');

      } catch (error) {
        console.error('导出Excel失败:', error);
        this.$message.error('导出数据时发生错误，请查看控制台');
      } finally {
        this.exportLoading = false;
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.course-rates-statistics {
  padding: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}

/* Optional: Style for button when export is loading */
.el-button:disabled {
  cursor: not-allowed;
}
</style> 
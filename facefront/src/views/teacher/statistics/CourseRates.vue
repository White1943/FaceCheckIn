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
import { getCourseAttendanceRates } from '@/api/attendance'
import { getTeacherCourses } from '@/api/course' // Assuming you have this API
import * as echarts from 'echarts'
import * as XLSX from 'xlsx'

export default {
  name: 'CourseRatesStatistics',
  data() {
    return {
      loading: false,
      chartData: [],
      teacherCourses: [],
      selectedCourseId: null,
      chartInstance: null
    }
  },
  async created() {
    await this.fetchTeacherCourses()
    this.fetchRates()
  },
  mounted() {
    this.initChart()
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
          // Reverse the data so older tasks appear first on the chart
          this.chartData = response.data.items.reverse()
          this.updateChart()
        } else {
          this.$message.error(response.message || '获取签到率数据失败')
        }
      } catch (error) {
        console.error('获取签到率数据失败:', error)
        this.$message.error('获取签到率数据失败')
      } finally {
        this.loading = false
      }
    },
    initChart() {
      const chartDom = this.$refs.chart
      if (chartDom) {
        this.chartInstance = echarts.init(chartDom)
        this.updateChart() // Initial empty chart setup
      }
    },
    updateChart() {
      if (!this.chartInstance) return

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
          data: this.chartData.map(item => `${item.date  }\n${  item.courseName.substring(0, 10)}`), // Combine date and course name for label
          axisLabel: {
             interval: 0, // Show all labels
             rotate: 15 // Rotate labels slightly if they overlap
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
          bottom: '10%', // Increase bottom margin for rotated labels
          containLabel: true
        },
        series: [
          {
            name: '签到率',
            type: 'bar', // Or 'line'
            barWidth: '60%',
            data: this.chartData.map(item => ({
                value: item.attendanceRate,
                // Store extra data for tooltip
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
        dataZoom: [ // Add data zoom for better navigation with many tasks
          {
            type: 'slider',
            start: 0,
            end: 100,
            bottom: 10
          },
          {
            type: 'inside',
            start: 0,
            end: 100
          }
        ],
      }
      this.chartInstance.setOption(option)
    },
    resizeChart() {
      if (this.chartInstance) {
        this.chartInstance.resize()
      }
    },
    handleExport() {
      if (this.chartData.length === 0) {
        this.$message.warning('没有数据可以导出');
        return;
      }

      try {
        // 1. Prepare data for worksheet
        const dataToExport = this.chartData.map(item => ({
          '课程名称': item.courseName,
          '任务时间': item.date, // Keep original date format from data
          '签到率 (%)': item.attendanceRate,
          '已签人数': item.checkedInCount,
          '应签人数': item.totalStudents
        }));

        // 2. Create worksheet from JSON data
        //    Headers are automatically derived from the keys of the first object
        const worksheet = XLSX.utils.json_to_sheet(dataToExport);

        // Optional: Adjust column widths (example)
        // worksheet['!cols'] = [
        //   { wch: 30 }, // Course Name
        //   { wch: 15 }, // Task Date
        //   { wch: 15 }, // Rate
        //   { wch: 10 }, // Checked In
        //   { wch: 10 }  // Total
        // ];

        // 3. Create a new workbook
        const workbook = XLSX.utils.book_new();

        // 4. Append the worksheet to the workbook
        XLSX.utils.book_append_sheet(workbook, worksheet, '课程签到率'); // Sheet name

        // 5. Generate and trigger download
        const fileName = `课程签到率统计_${new Date().toLocaleDateString()}.xlsx`;
        XLSX.writeFile(workbook, fileName);

        this.$message.success('数据导出成功！');

      } catch (error) {
        console.error('导出Excel失败:', error);
        this.$message.error('导出数据时发生错误，请查看控制台');
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
</style> 
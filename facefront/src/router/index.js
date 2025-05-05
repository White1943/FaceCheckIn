/**
 * @author https://github.com/zxwk1998/vue-admin-better （不想保留author可删除）
 * @description router全局配置，如有必要可分文件抽离，其中asyncRoutes只有在intelligence模式下才会用到，vip文档中已提供路由的基础图标与小清新图标的配置方案，请仔细阅读
 */

import Vue from 'vue'
import Router from 'vue-router'
import Layout from '@/layouts'
import EmptyLayout from '@/layouts/EmptyLayout'
import { publicPath, routerMode } from '@/config'

Vue.use(Router)
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true,
  },
  {
    path: '/register',
    component: () => import('@/views/register/index'),
    hidden: true,
  },
  {
    path: '/401',
    name: '401',
    component: () => import('@/views/401'),
    hidden: true,
  },
  {
    path: '/404',
    name: '404',
    component: () => import('@/views/404'),
    hidden: true,
  },
]

export const asyncRoutes = [
  {
    path: '/personalCenter',
    component: Layout,
    redirect: '/personalCenter/personalCenter',
    meta: { title: '个人中心', icon: 'user-circle', permissions: ['admin', 'teacher', 'student'] },
    children: [
      {
        path: 'personalCenter',
        name: 'PersonalCenter',
        component: () => import('@/views/personalCenter/index'),
        meta: { title: '个人中心' }, // Keep title for breadcrumb/tab
      },
    ],
  },

  // --- Flattened Teacher Routes ---
  {
    path: '/teacher/courses', // Full path for the menu item
    component: Layout,        // Must use Layout
    // No redirect needed if child path is empty or 'index'
    meta: { title: '我的课程', icon: 'book-open', roles: ['教师'], permissions: ['admin', 'teacher'] }, // Meta from original child
    children: [
      {
        path: '', // Empty path makes this the default view for /teacher/courses
        name: 'TeacherCourses',
        component: () => import('@/views/teacher/courses/index'),
        // Meta can be minimal here if parent handles title/icon
        meta: { title: '我的课程', noKeepAlive: true }
      }
    ]
  },
  // Hidden route for student management (needs Layout wrapper)
  {
     path: '/teacher/course_students_layout', // Needs a unique path for the layout wrapper
     component: Layout,
     hidden: true, // Hide this wrapper from sidebar
     meta: { roles: ['教师'], permissions: ['admin', 'teacher'] }, // Permissions needed on wrapper
        children: [
          {
           path: '/teacher/courses/:courseId/students', // Use the actual full path for the component
           name: 'TeacherCourseStudents',
           component: () => import('@/views/teacher/courses/CourseStudents'),
           meta: { title: '课程学生管理', noKeepAlive: true }, // Keep original meta for breadcrumb/tab
        }
     ]
  },
  {
    path: '/teacher/attendance',
    component: Layout,
    meta: { title: '考勤管理', icon: 'tasks', roles: ['教师'], permissions: ['admin', 'teacher'] },
    children: [
      {
          path: '', // Default view for /teacher/attendance
          name: 'TeacherAttendance',
          component: () => import('@/views/teacher/attendance/index'),
          meta: { title: '考勤管理', noKeepAlive: true }
       }
    ]
  },
  // Hidden route for task details (needs Layout wrapper)
   {
     path: '/teacher/attendance_details_layout',
     component: Layout,
     hidden: true,
     meta: { roles: ['教师'], permissions: ['admin', 'teacher'] },
     children: [
        {
           path: '/teacher/attendance/details/:taskId',
           name: 'TeacherTaskDetails',
           component: () => import('@/views/teacher/attendance/TaskDetails'),
           meta: { title: '签到详情', noKeepAlive: true },
           props: true // Keep props: true
        }
     ]
  },
  {
    path: '/teacher/attendance/appeals',
    component: Layout,
    meta: { title: '签到申诉处理', icon: 'exclamation-circle', roles: ['教师'], permissions: ['admin', 'teacher'] },
    children: [
      {
           path: '',
           name: 'TeacherAppeals',
           component: () => import('@/views/teacher/attendance/appeals'),
           meta: { title: '签到申诉处理', noKeepAlive: true }
        }
     ]
  },
  {
    path: '/teacher/statistics/rates',
    component: Layout,
    meta: { title: '签到率统计', icon: 'chart-bar', roles: ['教师'], permissions: ['admin', 'teacher'] },
    children: [
      {
           path: '',
           name: 'TeacherCourseRates',
           component: () => import('@/views/teacher/statistics/CourseRates'),
           meta: { title: '签到率统计', noKeepAlive: true }
        }
     ]
  },
  // --- End Flattened Teacher Routes ---


  // --- Flattened Student Routes ---
  {
    path: '/student/courses', // Full path
    component: Layout,
    meta: { title: '我的课程', icon: 'book-reader', permissions: ['admin', 'student'] }, // Use appropriate icon
    children: [
      {
        path: '',
        name: 'StudentCourses',
        component: () => import('@/views/student/courses/index'),
        meta: { title: '我的课程', noKeepAlive: true }
      },
    ]
  },
  {
    path: '/student/attendance',
    component: Layout,
    meta: { title: '我的考勤', icon: 'calendar-check', permissions: ['admin', 'student'] }, // Use appropriate icon
    children: [
      {
        path: '',
        name: 'StudentAttendance',
        component: () => import('@/views/student/attendance/index'),
        meta: { title: '我的考勤', noKeepAlive: true }
      },
    ]
  },
  {
    path: '/student/appeals',
    component: Layout,
    meta: { title: '申诉管理', icon: 'file-signature', permissions: ['admin', 'student'] }, // Use appropriate icon
    children: [
      {
        path: '',
        name: 'StudentAppeals',
        component: () => import('@/views/student/attendance/appeals'),
        meta: { title: '申诉管理', noKeepAlive: true }
      },
    ]
  },
  // --- End Flattened Student Routes ---

  // --- Admin Routes (Example - Assuming they might also be flattened or kept as is) ---
  // If you want to flatten Admin routes, follow the same pattern
  // Example: Keeping Admin nested (if desired)
  {
     path: '/admin',
     component: Layout,
     redirect: '/admin/users', // Redirect to the first admin page
     meta: { title: '系统管理', icon: 'cog', permissions: ['admin'] }, // Only admin
     children: [
       {
         path: 'users',
         name: 'AdminUsers',
         component: () => import('@/views/admin/users/index'), // Adjust path if needed
         meta: { title: '用户管理', icon: 'users-cog' }
       },
       // Add other admin sub-routes here
     ]
   },
  // --- End Admin Routes ---

  { path: '*', redirect: '/404', hidden: true },
]

const router = new Router({
  base: publicPath,
  mode: routerMode,
  scrollBehavior: () => ({
    y: 0,
  }),
  routes: constantRoutes,
})

export function resetRouter() {
  location.reload()
}

export default router

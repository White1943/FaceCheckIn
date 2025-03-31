/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 80022
Source Host           : localhost:3306
Source Database       : facecheckin

Target Server Type    : MYSQL
Target Server Version : 80022
File Encoding         : 65001

Date: 2025-03-31 11:41:30
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for attendance_records
-- ----------------------------
DROP TABLE IF EXISTS `attendance_records`;
CREATE TABLE `attendance_records` (
  `record_id` int NOT NULL AUTO_INCREMENT,
  `course_id` int NOT NULL,
  `student_id` int NOT NULL,
  `check_in_time` timestamp NULL DEFAULT NULL,
  `check_in_type` enum('正常','迟到','缺课') NOT NULL,
  `location_lat` decimal(10,7) DEFAULT NULL,
  `location_lng` decimal(10,7) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `task_id` int NOT NULL,
  `face_image` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`record_id`),
  KEY `course_id` (`course_id`),
  KEY `student_id` (`student_id`),
  KEY `fk_task_id` (`task_id`),
  CONSTRAINT `attendance_records_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) ON DELETE CASCADE,
  CONSTRAINT `attendance_records_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_task_id` FOREIGN KEY (`task_id`) REFERENCES `attendance_tasks` (`task_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of attendance_records
-- ----------------------------
INSERT INTO `attendance_records` VALUES ('1', '1', '1', '2025-03-11 23:28:00', '缺课', null, null, '2025-03-11 23:39:04', '3', null);
INSERT INTO `attendance_records` VALUES ('2', '1', '1', '2025-03-11 20:42:00', '缺课', null, null, '2025-03-11 23:39:04', '1', null);
INSERT INTO `attendance_records` VALUES ('3', '2', '1', '2025-03-11 23:39:11', '迟到', null, null, '2025-03-11 23:39:11', '4', null);
INSERT INTO `attendance_records` VALUES ('4', '1', '1', '2025-03-11 23:28:00', '缺课', null, null, '2025-03-11 23:40:07', '2', null);
INSERT INTO `attendance_records` VALUES ('5', '2', '1', '2025-03-11 23:45:45', '迟到', null, null, '2025-03-11 23:45:45', '5', null);
INSERT INTO `attendance_records` VALUES ('6', '2', '1', '2025-03-11 23:49:16', '迟到', null, null, '2025-03-11 23:49:16', '6', null);
INSERT INTO `attendance_records` VALUES ('7', '2', '1', '2025-03-11 23:55:03', '正常', null, null, '2025-03-11 23:55:03', '7', null);
INSERT INTO `attendance_records` VALUES ('8', '2', '1', '2025-03-17 16:18:39', '正常', null, null, '2025-03-17 16:18:39', '8', null);
INSERT INTO `attendance_records` VALUES ('9', '1', '3', '2025-03-11 23:28:00', '缺课', null, null, '2025-03-30 01:18:26', '2', null);
INSERT INTO `attendance_records` VALUES ('10', '1', '3', '2025-03-11 23:28:00', '缺课', null, null, '2025-03-30 01:18:26', '3', null);
INSERT INTO `attendance_records` VALUES ('11', '1', '3', '2025-03-11 20:42:00', '缺课', null, null, '2025-03-30 01:18:26', '1', null);
INSERT INTO `attendance_records` VALUES ('12', '5', '1', '2025-03-30 00:30:00', '缺课', null, null, '2025-03-30 23:51:01', '9', null);
INSERT INTO `attendance_records` VALUES ('13', '1', '3', '2025-03-31 10:52:03', '迟到', null, null, '2025-03-31 10:52:09', '15', '3_15_1743389522.jpg');
INSERT INTO `attendance_records` VALUES ('14', '1', '3', '2025-03-31 10:56:14', '迟到', null, null, '2025-03-31 10:56:15', '16', '3_16_1743389773.jpg');
INSERT INTO `attendance_records` VALUES ('15', '1', '3', '2025-03-31 10:59:54', '迟到', null, null, '2025-03-31 10:59:56', '17', '3_17_1743389994.jpg');
INSERT INTO `attendance_records` VALUES ('16', '1', '3', '2025-03-31 11:35:16', '正常', null, null, '2025-03-31 11:35:28', '18', '3_18_1743392116.jpg');

-- ----------------------------
-- Table structure for attendance_tasks
-- ----------------------------
DROP TABLE IF EXISTS `attendance_tasks`;
CREATE TABLE `attendance_tasks` (
  `task_id` int NOT NULL AUTO_INCREMENT,
  `course_id` int NOT NULL,
  `teacher_id` int NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `location_lat` decimal(10,7) DEFAULT NULL,
  `location_lng` decimal(10,7) DEFAULT NULL,
  `status` enum('active','ended','cancelled') NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`task_id`),
  KEY `course_id` (`course_id`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `attendance_tasks_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) ON DELETE CASCADE,
  CONSTRAINT `attendance_tasks_ibfk_2` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of attendance_tasks
-- ----------------------------
INSERT INTO `attendance_tasks` VALUES ('1', '1', '1', '2025-03-11 19:42:00', '2025-03-11 20:42:00', null, null, 'ended', '2025-03-11 20:45:51');
INSERT INTO `attendance_tasks` VALUES ('2', '1', '1', '2025-03-11 22:27:00', '2025-03-11 23:28:00', null, null, 'ended', '2025-03-11 22:28:18');
INSERT INTO `attendance_tasks` VALUES ('3', '1', '1', '2025-03-11 22:27:00', '2025-03-11 23:28:00', null, null, 'ended', '2025-03-11 22:28:18');
INSERT INTO `attendance_tasks` VALUES ('4', '2', '1', '2025-03-11 23:15:00', '2025-03-11 23:54:00', null, null, 'ended', '2025-03-11 23:17:58');
INSERT INTO `attendance_tasks` VALUES ('5', '2', '1', '2025-03-11 23:45:00', '2025-03-11 23:58:00', null, null, 'ended', '2025-03-11 23:45:39');
INSERT INTO `attendance_tasks` VALUES ('6', '2', '1', '2025-03-11 23:47:00', '2025-03-11 23:59:00', null, null, 'ended', '2025-03-11 23:48:32');
INSERT INTO `attendance_tasks` VALUES ('7', '2', '1', '2025-03-11 23:54:00', '2025-03-11 23:59:00', null, null, 'ended', '2025-03-11 23:54:51');
INSERT INTO `attendance_tasks` VALUES ('8', '2', '1', '2025-03-17 16:18:00', '2025-03-17 16:28:00', null, null, 'ended', '2025-03-17 16:18:08');
INSERT INTO `attendance_tasks` VALUES ('9', '5', '1', '2025-03-30 00:02:00', '2025-03-30 00:30:00', null, null, 'ended', '2025-03-30 00:02:40');
INSERT INTO `attendance_tasks` VALUES ('10', '1', '1', '2025-03-30 01:05:00', '2025-03-30 06:17:00', null, null, 'active', '2025-03-30 01:05:50');
INSERT INTO `attendance_tasks` VALUES ('11', '1', '1', '2025-03-30 01:10:00', '2025-03-30 02:10:00', null, null, 'active', '2025-03-30 01:10:09');
INSERT INTO `attendance_tasks` VALUES ('12', '4', '1', '2025-03-30 22:07:00', '2025-03-30 23:07:00', null, null, 'active', '2025-03-30 22:07:18');
INSERT INTO `attendance_tasks` VALUES ('13', '2', '1', '2025-03-30 22:54:00', '2025-03-30 23:54:00', null, null, 'active', '2025-03-30 22:54:27');
INSERT INTO `attendance_tasks` VALUES ('14', '4', '1', '2025-03-30 23:22:00', '2025-03-30 23:54:00', null, null, 'active', '2025-03-30 23:22:35');
INSERT INTO `attendance_tasks` VALUES ('15', '1', '1', '2025-03-31 00:04:00', '2025-03-31 23:04:00', null, null, 'ended', '2025-03-31 00:04:17');
INSERT INTO `attendance_tasks` VALUES ('16', '1', '1', '2025-03-31 10:54:00', '2025-03-31 16:54:00', null, null, 'ended', '2025-03-31 10:54:30');
INSERT INTO `attendance_tasks` VALUES ('17', '1', '1', '2025-03-31 10:58:00', '2025-03-31 15:59:00', null, null, 'active', '2025-03-31 10:59:10');
INSERT INTO `attendance_tasks` VALUES ('18', '1', '1', '2025-03-31 11:32:00', '2025-03-31 12:32:00', null, null, 'active', '2025-03-31 11:32:55');

-- ----------------------------
-- Table structure for courses
-- ----------------------------
DROP TABLE IF EXISTS `courses`;
CREATE TABLE `courses` (
  `course_id` int NOT NULL AUTO_INCREMENT,
  `course_name` varchar(100) NOT NULL,
  `teacher_id` int NOT NULL,
  `semester` varchar(20) NOT NULL,
  `description` text,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `location` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`course_id`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `courses_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of courses
-- ----------------------------
INSERT INTO `courses` VALUES ('1', '数据结构', '1', '25a', '11', '08:15:00', '09:45:00', '松2110', '2025-03-09 23:34:14');
INSERT INTO `courses` VALUES ('2', '大物实验', '1', '24a', '实验报告课上提交当等待', '10:05:00', '11:35:00', '综合楼203', '2025-03-09 23:36:00');
INSERT INTO `courses` VALUES ('4', '数据库', '1', '2025a1', 'mysql数据库', '15:00:00', '16:30:00', '松2102', '2025-03-17 16:24:06');
INSERT INTO `courses` VALUES ('5', '计算机网络', '1', '2025a', '', '08:15:00', '09:45:00', '松2204', '2025-03-17 19:45:04');

-- ----------------------------
-- Table structure for course_students
-- ----------------------------
DROP TABLE IF EXISTS `course_students`;
CREATE TABLE `course_students` (
  `course_id` int NOT NULL,
  `student_id` int NOT NULL,
  `join_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`course_id`,`student_id`),
  KEY `student_id` (`student_id`),
  CONSTRAINT `course_students_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) ON DELETE CASCADE,
  CONSTRAINT `course_students_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of course_students
-- ----------------------------
INSERT INTO `course_students` VALUES ('1', '1', '2025-03-11 22:25:38');
INSERT INTO `course_students` VALUES ('1', '3', '2025-03-30 01:07:43');
INSERT INTO `course_students` VALUES ('2', '1', '2025-03-11 22:25:46');
INSERT INTO `course_students` VALUES ('4', '3', '2025-03-30 22:07:33');
INSERT INTO `course_students` VALUES ('5', '1', '2025-03-30 00:02:51');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `real_name` varchar(50) NOT NULL,
  `role` enum('教师','学生','管理员') NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `status` tinyint DEFAULT '1',
  `avatar` varchar(255) DEFAULT '/avatar2.jpg',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES ('1', '小马', 'scrypt:32768:8:1$XArgmHAnkAnF7D9t$4fedf1d1be013e1e2ea0adefe388a1ef502649c012ee2415a7ad86dc17f39a5027d25bd7415d149cb549ffe28605f7d9e1a251fc9ce5ab757fdf8078207abbaa', '小马real', '管理员', 'hheeh@qq.com', '1', '/static/images/avatars/avatar_1_1743392408.jpg');
INSERT INTO `users` VALUES ('2', '头像测试', 'scrypt:32768:8:1$CrmghDoWpc7cNVmY$f2140afdfe56e0bf3f3f5d9d2b24b161d3b13c7f3905aa912bd88c3d63f946eed68e7cfba7cc5fb423cb2c30fb018e825ce374bf2397e3116bdac09d37cc98a2', '信息', '管理员', null, '1', '/avatar1.jpg');
INSERT INTO `users` VALUES ('3', 'huge', 'scrypt:32768:8:1$CshMbmk5w5JgtViW$801c8658a2ad5a0905276b6c6ebd91e24454f27f1205abed3850c742531c1dabb2e7475d0253511a1cadbd4b323defec46337b0555a57fecc488ce60b46a77e4', '胡歌', '学生', null, '1', '/static/images/avatars/avatar_3_1743389856.jpg');

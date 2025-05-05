/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 80022
Source Host           : localhost:3306
Source Database       : facecheckin

Target Server Type    : MYSQL
Target Server Version : 80022
File Encoding         : 65001

Date: 2025-05-01 10:22:57
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
  `check_in_type` enum('正常','迟到','缺课','异常') NOT NULL,
  `location_lat` decimal(10,7) DEFAULT NULL,
  `location_lng` decimal(10,7) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `task_id` int NOT NULL,
  `face_image` varchar(255) DEFAULT NULL,
  `review_status` enum('未申诉','待审核','已审核') NOT NULL DEFAULT '未申诉',
  `appeal_reason` text,
  PRIMARY KEY (`record_id`),
  KEY `course_id` (`course_id`),
  KEY `student_id` (`student_id`),
  KEY `fk_task_id` (`task_id`),
  CONSTRAINT `attendance_records_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`course_id`) ON DELETE CASCADE,
  CONSTRAINT `attendance_records_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_task_id` FOREIGN KEY (`task_id`) REFERENCES `attendance_tasks` (`task_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=72 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of attendance_records
-- ----------------------------
INSERT INTO `attendance_records` VALUES ('1', '1', '1', '2025-03-11 23:28:00', '缺课', null, null, '2025-03-11 23:39:04', '3', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('2', '1', '1', '2025-03-11 20:42:00', '缺课', null, null, '2025-03-11 23:39:04', '1', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('3', '2', '1', '2025-03-11 23:39:11', '迟到', null, null, '2025-03-11 23:39:11', '4', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('4', '1', '1', '2025-03-11 23:28:00', '缺课', null, null, '2025-03-11 23:40:07', '2', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('5', '2', '1', '2025-03-11 23:45:45', '迟到', null, null, '2025-03-11 23:45:45', '5', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('6', '2', '1', '2025-03-11 23:49:16', '迟到', null, null, '2025-03-11 23:49:16', '6', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('7', '2', '1', '2025-03-11 23:55:03', '正常', null, null, '2025-03-11 23:55:03', '7', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('8', '2', '1', '2025-03-17 16:18:39', '正常', null, null, '2025-03-17 16:18:39', '8', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('9', '1', '3', '2025-03-11 23:28:00', '缺课', null, null, '2025-03-30 01:18:26', '2', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('10', '1', '3', '2025-03-11 23:28:00', '缺课', null, null, '2025-03-30 01:18:26', '3', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('11', '1', '3', '2025-03-11 20:42:00', '缺课', null, null, '2025-03-30 01:18:26', '1', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('12', '5', '1', '2025-03-30 00:30:00', '缺课', null, null, '2025-03-30 23:51:01', '9', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('13', '1', '3', '2025-03-31 10:52:03', '迟到', null, null, '2025-03-31 10:52:09', '15', '3_15_1743389522.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('14', '1', '3', '2025-03-31 10:56:14', '迟到', null, null, '2025-03-31 10:56:15', '16', '3_16_1743389773.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('15', '1', '3', '2025-03-31 10:59:54', '迟到', null, null, '2025-03-31 10:59:56', '17', '3_17_1743389994.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('16', '1', '3', '2025-03-31 11:35:16', '正常', null, null, '2025-03-31 11:35:28', '18', '3_18_1743392116.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('17', '1', '3', '2025-03-31 14:48:16', '正常', null, null, '2025-03-31 14:48:28', '19', '3_19_1743403696.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('18', '1', '3', '2025-03-31 14:49:36', '正常', null, null, '2025-03-31 14:49:37', '20', '3_20_1743403776.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('19', '1', '3', '2025-03-31 17:26:12', '正常', null, null, '2025-03-31 17:26:13', '21', '3_21_1743413171.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('20', '1', '3', '2025-03-31 22:23:27', '正常', null, null, '2025-03-31 22:23:28', '22', '3_22_1743431007.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('21', '1', '3', '2025-04-01 21:42:15', '正常', null, null, '2025-04-01 21:42:30', '23', '3_23_1743514935.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('22', '1', '3', '2025-04-01 21:49:31', '正常', null, null, '2025-04-01 21:49:34', '24', '3_24_1743515371.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('23', '1', '3', '2025-04-01 21:51:06', '正常', null, null, '2025-04-01 21:51:17', '25', '3_25_1743515466.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('24', '1', '3', '2025-04-01 21:59:32', '正常', null, null, '2025-04-01 21:59:38', '26', '3_26_1743515971.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('25', '1', '1', '2025-04-01 23:51:00', '缺课', null, null, '2025-04-01 23:03:02', '26', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('26', '1', '1', '2025-03-31 22:27:00', '缺课', null, null, '2025-04-01 23:03:02', '22', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('27', '1', '1', '2025-03-31 18:21:00', '缺课', null, null, '2025-04-01 23:03:02', '21', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('28', '1', '1', '2025-03-31 16:54:00', '缺课', null, null, '2025-04-01 23:03:02', '16', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('29', '1', '1', '2025-03-31 23:04:00', '缺课', null, null, '2025-04-01 23:03:02', '15', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('30', '1', '3', '2025-04-01 23:06:32', '正常', null, null, '2025-04-01 23:06:35', '29', '3_29_1743519991.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('31', '1', '1', '2025-04-03 23:05:45', '迟到', '0.0000000', '0.0000000', '2025-04-03 23:05:51', '31', '1_31_1743692744.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('32', '7', '1', '2025-04-05 22:05:36', '正常', '0.0000000', '0.0000000', '2025-04-05 22:05:50', '32', '1_32_1743861936.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('33', '7', '1', '2025-04-05 22:09:57', '迟到', '0.0000000', '0.0000000', '2025-04-05 22:09:58', '33', '1_33_1743862197.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('34', '7', '1', '2025-04-05 22:19:15', '正常', '0.0000000', '0.0000000', '2025-04-05 22:19:16', '34', '1_34_1743862755.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('35', '7', '3', '2025-04-05 23:11:59', '迟到', '0.0000000', '0.0000000', '2025-04-05 23:12:22', '34', '3_34_1743865918.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('36', '7', '3', '2025-04-05 23:06:00', '缺课', null, null, '2025-04-05 23:12:29', '33', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('37', '7', '3', '2025-04-05 23:56:00', '缺课', null, null, '2025-04-05 23:12:29', '32', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('38', '1', '3', '2025-04-03 23:36:00', '缺课', null, null, '2025-04-05 23:12:29', '31', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('39', '7', '1', '2025-04-05 23:28:26', '正常', '0.0000000', '0.0000000', '2025-04-05 23:28:33', '35', '1_35_1743866906.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('40', '1', '1', '2025-04-03 22:26:00', '缺课', null, null, '2025-04-06 00:14:49', '30', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('41', '1', '1', '2025-04-01 23:23:00', '缺课', null, null, '2025-04-06 00:14:49', '29', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('42', '1', '1', '2025-04-01 23:03:00', '缺课', null, null, '2025-04-06 00:14:49', '28', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('43', '1', '1', '2025-04-01 22:52:00', '缺课', null, null, '2025-04-06 00:14:49', '27', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('44', '1', '1', '2025-04-01 22:50:00', '缺课', null, null, '2025-04-06 00:14:49', '25', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('45', '1', '1', '2025-04-01 22:44:00', '缺课', null, null, '2025-04-06 00:14:49', '24', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('46', '1', '1', '2025-04-01 22:41:00', '缺课', null, null, '2025-04-06 00:14:49', '23', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('47', '1', '1', '2025-03-31 15:49:00', '缺课', null, null, '2025-04-06 00:14:49', '20', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('48', '1', '1', '2025-03-31 15:44:00', '缺课', null, null, '2025-04-06 00:14:49', '19', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('49', '1', '1', '2025-03-31 12:32:00', '缺课', null, null, '2025-04-06 00:14:49', '18', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('50', '1', '1', '2025-03-31 15:59:00', '缺课', null, null, '2025-04-06 00:14:49', '17', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('51', '2', '1', '2025-03-30 23:54:00', '缺课', null, null, '2025-04-06 00:14:49', '13', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('52', '1', '1', '2025-03-30 02:10:00', '缺课', null, null, '2025-04-06 00:14:49', '11', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('53', '1', '1', '2025-03-30 06:17:00', '缺课', null, null, '2025-04-06 00:14:49', '10', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('54', '7', '1', '2025-04-06 00:21:40', '正常', '0.0000000', '0.0000000', '2025-04-06 00:21:41', '37', '1_37_1743870100.jpg', '已审核', '系统自动申诉: 连续三次人脸识别失败');
INSERT INTO `attendance_records` VALUES ('55', '7', '3', '2025-04-06 00:23:40', '异常', '0.0000000', '0.0000000', '2025-04-06 00:23:41', '37', '3_37_1743870220.jpg', '待审核', '系统自动申诉: 连续三次人脸识别失败');
INSERT INTO `attendance_records` VALUES ('56', '7', '1', '2025-04-06 00:26:22', '异常', '0.0000000', '0.0000000', '2025-04-06 00:26:23', '38', '1_38_1743870381.jpg', '已审核', '系统自动申诉: 连续三次人脸识别失败');
INSERT INTO `attendance_records` VALUES ('57', '7', '1', '2025-04-10 18:05:03', '异常', '0.0000000', '0.0000000', '2025-04-10 18:05:04', '39', '1_39_1744279503.jpg', '待审核', '系统自动申诉: 连续三次人脸识别失败');
INSERT INTO `attendance_records` VALUES ('58', '7', '1', '2025-04-05 23:58:00', '缺课', null, null, '2025-04-10 18:06:21', '36', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('59', '10', '6', '2025-04-16 01:01:00', '缺课', null, null, '2025-04-16 11:19:56', '47', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('60', '4', '6', '2025-03-30 23:54:00', '缺课', null, null, '2025-04-16 11:19:56', '14', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('61', '4', '6', '2025-03-30 23:07:00', '缺课', null, null, '2025-04-16 11:19:56', '12', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('62', '10', '6', '2025-04-16 11:21:58', '正常', '0.0000000', '0.0000000', '2025-04-16 11:21:59', '48', '6_48_1744773717.jpg', '已审核', '系统自动申诉: 连续三次人脸识别失败');
INSERT INTO `attendance_records` VALUES ('63', '10', '6', '2025-04-16 12:04:06', '正常', '0.0000000', '0.0000000', '2025-04-16 12:04:07', '49', '6_49_1744776245.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('64', '10', '6', '2025-04-17 20:33:10', '正常', '0.0000000', '0.0000000', '2025-04-17 20:33:24', '50', '6_50_1744893189.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('65', '14', '6', '2025-04-17 20:50:04', '异常', '0.0000000', '0.0000000', '2025-04-17 20:50:06', '51', '6_51_1744894204.jpg', '待审核', '系统自动申诉: 连续三次人脸识别失败');
INSERT INTO `attendance_records` VALUES ('66', '14', '7', '2025-04-17 20:52:05', '正常', '0.0000000', '0.0000000', '2025-04-17 20:52:06', '51', '7_51_1744894324.jpg', '未申诉', null);
INSERT INTO `attendance_records` VALUES ('67', '10', '7', '2025-04-16 13:39:00', '缺课', null, null, '2025-04-17 20:52:09', '49', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('68', '10', '7', '2025-04-16 12:42:00', '缺课', null, null, '2025-04-17 20:52:09', '48', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('69', '10', '7', '2025-04-16 01:01:00', '缺课', null, null, '2025-04-17 20:52:09', '47', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('70', '11', '7', '2025-04-16 01:37:00', '缺课', null, null, '2025-04-17 20:52:09', '46', null, '未申诉', null);
INSERT INTO `attendance_records` VALUES ('71', '14', '6', '2025-04-18 23:02:33', '正常', '0.0000000', '0.0000000', '2025-04-18 23:02:34', '53', '6_53_1744988552.jpg', '已审核', '系统自动申诉: 连续三次人脸识别失败');

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
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8;

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
INSERT INTO `attendance_tasks` VALUES ('10', '1', '1', '2025-03-30 01:05:00', '2025-03-30 06:17:00', null, null, 'ended', '2025-03-30 01:05:50');
INSERT INTO `attendance_tasks` VALUES ('11', '1', '1', '2025-03-30 01:10:00', '2025-03-30 02:10:00', null, null, 'ended', '2025-03-30 01:10:09');
INSERT INTO `attendance_tasks` VALUES ('12', '4', '1', '2025-03-30 22:07:00', '2025-03-30 23:07:00', null, null, 'ended', '2025-03-30 22:07:18');
INSERT INTO `attendance_tasks` VALUES ('13', '2', '1', '2025-03-30 22:54:00', '2025-03-30 23:54:00', null, null, 'ended', '2025-03-30 22:54:27');
INSERT INTO `attendance_tasks` VALUES ('14', '4', '1', '2025-03-30 23:22:00', '2025-03-30 23:54:00', null, null, 'ended', '2025-03-30 23:22:35');
INSERT INTO `attendance_tasks` VALUES ('15', '1', '1', '2025-03-31 00:04:00', '2025-03-31 23:04:00', null, null, 'ended', '2025-03-31 00:04:17');
INSERT INTO `attendance_tasks` VALUES ('16', '1', '1', '2025-03-31 10:54:00', '2025-03-31 16:54:00', null, null, 'ended', '2025-03-31 10:54:30');
INSERT INTO `attendance_tasks` VALUES ('17', '1', '1', '2025-03-31 10:58:00', '2025-03-31 15:59:00', null, null, 'ended', '2025-03-31 10:59:10');
INSERT INTO `attendance_tasks` VALUES ('18', '1', '1', '2025-03-31 11:32:00', '2025-03-31 12:32:00', null, null, 'ended', '2025-03-31 11:32:55');
INSERT INTO `attendance_tasks` VALUES ('19', '1', '1', '2025-03-31 14:44:00', '2025-03-31 15:44:00', null, null, 'ended', '2025-03-31 14:44:57');
INSERT INTO `attendance_tasks` VALUES ('20', '1', '1', '2025-03-31 14:49:00', '2025-03-31 15:49:00', null, null, 'ended', '2025-03-31 14:49:19');
INSERT INTO `attendance_tasks` VALUES ('21', '1', '1', '2025-03-31 17:21:00', '2025-03-31 18:21:00', null, null, 'ended', '2025-03-31 17:21:57');
INSERT INTO `attendance_tasks` VALUES ('22', '1', '1', '2025-03-31 22:20:00', '2025-03-31 22:27:00', null, null, 'ended', '2025-03-31 22:20:18');
INSERT INTO `attendance_tasks` VALUES ('23', '1', '1', '2025-04-01 21:38:00', '2025-04-01 22:41:00', null, null, 'ended', '2025-04-01 21:41:45');
INSERT INTO `attendance_tasks` VALUES ('24', '1', '1', '2025-04-01 21:44:00', '2025-04-01 22:44:00', null, null, 'ended', '2025-04-01 21:44:38');
INSERT INTO `attendance_tasks` VALUES ('25', '1', '1', '2025-04-01 21:50:00', '2025-04-01 22:50:00', null, null, 'ended', '2025-04-01 21:50:27');
INSERT INTO `attendance_tasks` VALUES ('26', '1', '1', '2025-04-01 22:48:00', '2025-04-01 23:51:00', null, null, 'ended', '2025-04-01 21:51:41');
INSERT INTO `attendance_tasks` VALUES ('27', '1', '1', '2025-04-01 21:52:00', '2025-04-01 22:52:00', null, null, 'ended', '2025-04-01 21:52:44');
INSERT INTO `attendance_tasks` VALUES ('28', '1', '1', '2025-04-01 22:03:00', '2025-04-01 23:03:00', null, null, 'ended', '2025-04-01 23:04:05');
INSERT INTO `attendance_tasks` VALUES ('29', '1', '1', '2025-04-01 23:05:00', '2025-04-01 23:23:00', null, null, 'ended', '2025-04-01 23:06:11');
INSERT INTO `attendance_tasks` VALUES ('30', '1', '1', '2025-04-03 20:26:00', '2025-04-03 22:26:00', null, null, 'ended', '2025-04-03 20:26:46');
INSERT INTO `attendance_tasks` VALUES ('31', '1', '1', '2025-04-03 21:36:00', '2025-04-03 23:36:00', null, null, 'ended', '2025-04-03 22:37:01');
INSERT INTO `attendance_tasks` VALUES ('32', '7', '1', '2025-04-05 21:56:00', '2025-04-05 23:56:00', null, null, 'ended', '2025-04-05 21:56:48');
INSERT INTO `attendance_tasks` VALUES ('33', '7', '1', '2025-04-05 20:07:00', '2025-04-05 23:06:00', null, null, 'ended', '2025-04-05 22:07:15');
INSERT INTO `attendance_tasks` VALUES ('34', '7', '1', '2025-04-05 22:18:00', '2025-04-05 23:18:00', null, null, 'ended', '2025-04-05 22:18:38');
INSERT INTO `attendance_tasks` VALUES ('35', '7', '1', '2025-04-05 23:24:00', '2025-04-05 23:59:00', null, null, 'ended', '2025-04-05 23:27:59');
INSERT INTO `attendance_tasks` VALUES ('36', '7', '1', '2025-04-05 23:37:00', '2025-04-05 23:58:00', null, null, 'ended', '2025-04-05 23:38:01');
INSERT INTO `attendance_tasks` VALUES ('37', '7', '1', '2025-04-06 00:18:00', '2025-04-06 02:18:00', null, null, 'ended', '2025-04-06 00:18:25');
INSERT INTO `attendance_tasks` VALUES ('38', '7', '1', '2025-04-06 00:24:00', '2025-04-06 00:44:00', null, null, 'ended', '2025-04-06 00:25:07');
INSERT INTO `attendance_tasks` VALUES ('39', '7', '1', '2025-04-10 17:32:00', '2025-04-10 19:32:00', null, null, 'ended', '2025-04-10 17:32:57');
INSERT INTO `attendance_tasks` VALUES ('40', '7', '1', '2025-04-10 18:04:00', '2025-04-10 18:07:00', null, null, 'ended', '2025-04-10 18:06:53');
INSERT INTO `attendance_tasks` VALUES ('41', '7', '1', '2025-04-10 18:08:00', '2025-04-10 18:11:00', null, null, 'ended', '2025-04-10 18:10:10');
INSERT INTO `attendance_tasks` VALUES ('42', '7', '1', '2025-04-10 18:00:00', '2025-04-10 18:11:00', null, null, 'ended', '2025-04-10 18:10:25');
INSERT INTO `attendance_tasks` VALUES ('43', '7', '1', '2025-04-10 18:13:00', '2025-04-10 18:15:00', null, null, 'ended', '2025-04-10 18:13:32');
INSERT INTO `attendance_tasks` VALUES ('44', '7', '1', '2025-04-10 18:00:00', '2025-04-10 18:15:00', null, null, 'ended', '2025-04-10 18:13:46');
INSERT INTO `attendance_tasks` VALUES ('45', '7', '1', '2025-04-15 22:24:00', '2025-04-15 23:24:00', null, null, 'ended', '2025-04-15 22:24:25');
INSERT INTO `attendance_tasks` VALUES ('46', '11', '5', '2025-04-16 00:37:00', '2025-04-16 01:37:00', null, null, 'ended', '2025-04-16 00:37:08');
INSERT INTO `attendance_tasks` VALUES ('47', '10', '5', '2025-04-16 00:37:00', '2025-04-16 01:01:00', null, null, 'ended', '2025-04-16 00:37:23');
INSERT INTO `attendance_tasks` VALUES ('48', '10', '5', '2025-04-16 10:42:00', '2025-04-16 12:42:00', null, null, 'ended', '2025-04-16 10:42:41');
INSERT INTO `attendance_tasks` VALUES ('49', '10', '5', '2025-04-16 11:39:00', '2025-04-16 13:39:00', null, null, 'ended', '2025-04-16 11:39:25');
INSERT INTO `attendance_tasks` VALUES ('50', '10', '5', '2025-04-17 20:32:00', '2025-04-17 21:32:00', null, null, 'ended', '2025-04-17 20:32:14');
INSERT INTO `attendance_tasks` VALUES ('51', '14', '5', '2025-04-17 20:46:00', '2025-04-17 21:49:00', null, null, 'ended', '2025-04-17 20:49:24');
INSERT INTO `attendance_tasks` VALUES ('52', '14', '5', '2025-04-18 23:00:00', '2025-04-18 23:01:00', null, null, 'ended', '2025-04-18 23:00:11');
INSERT INTO `attendance_tasks` VALUES ('53', '14', '5', '2025-04-18 23:01:00', '2025-04-18 23:08:00', null, null, 'ended', '2025-04-18 23:01:28');

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
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of courses
-- ----------------------------
INSERT INTO `courses` VALUES ('1', '数据结构', '1', '25a', '11', '08:15:00', '09:45:00', '松2110', '2025-03-09 23:34:14');
INSERT INTO `courses` VALUES ('2', '大物实验', '1', '24a', '实验报告课上提交当等待', '10:05:00', '11:35:00', '综合楼203', '2025-03-09 23:36:00');
INSERT INTO `courses` VALUES ('4', '数据库', '1', '2025a1', 'mysql数据库', '15:00:00', '16:30:00', '松2102', '2025-03-17 16:24:06');
INSERT INTO `courses` VALUES ('5', '计算机网络', '1', '2025a', '', '08:15:00', '09:45:00', '松2204', '2025-03-17 19:45:04');
INSERT INTO `courses` VALUES ('6', '教师测试', '4', '25上', '', '10:05:00', '11:35:00', '松3022', '2025-03-31 16:31:45');
INSERT INTO `courses` VALUES ('7', 'dd', '1', '25下', '对的', '10:05:00', '11:35:00', '松222', '2025-04-01 23:01:39');
INSERT INTO `courses` VALUES ('10', '自习', '5', '23', '所示', '08:15:00', '09:45:00', '松2322', '2025-04-16 00:27:14');
INSERT INTO `courses` VALUES ('11', '自习2', '5', '23', '', '15:00:00', '16:30:00', '延3322', '2025-04-16 00:36:34');
INSERT INTO `courses` VALUES ('13', '自习3', '5', '23', '', '08:15:00', '09:45:00', '松3222', '2025-04-16 12:05:12');
INSERT INTO `courses` VALUES ('14', '高等数学', '5', '25上', '欢迎大家选修我（教师）所授的高等数学', '08:15:00', '09:45:00', '松2222', '2025-04-17 20:48:41');

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
INSERT INTO `course_students` VALUES ('4', '6', '2025-04-16 10:59:58');
INSERT INTO `course_students` VALUES ('5', '1', '2025-03-30 00:02:51');
INSERT INTO `course_students` VALUES ('7', '1', '2025-04-05 21:57:01');
INSERT INTO `course_students` VALUES ('7', '3', '2025-04-05 23:11:15');
INSERT INTO `course_students` VALUES ('10', '6', '2025-04-16 10:59:35');
INSERT INTO `course_students` VALUES ('10', '7', '2025-04-16 11:59:31');
INSERT INTO `course_students` VALUES ('11', '7', '2025-04-16 11:59:28');
INSERT INTO `course_students` VALUES ('14', '6', '2025-04-17 20:48:57');
INSERT INTO `course_students` VALUES ('14', '7', '2025-04-17 20:49:08');

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
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES ('1', '小马', 'scrypt:32768:8:1$XArgmHAnkAnF7D9t$4fedf1d1be013e1e2ea0adefe388a1ef502649c012ee2415a7ad86dc17f39a5027d25bd7415d149cb549ffe28605f7d9e1a251fc9ce5ab757fdf8078207abbaa', '小马real', '管理员', 'hheeh@qq.com', '1', '/static/images/avatars/avatar_1_1743689945.jpg');
INSERT INTO `users` VALUES ('2', '头像测试', 'scrypt:32768:8:1$CrmghDoWpc7cNVmY$f2140afdfe56e0bf3f3f5d9d2b24b161d3b13c7f3905aa912bd88c3d63f946eed68e7cfba7cc5fb423cb2c30fb018e825ce374bf2397e3116bdac09d37cc98a2', '信息', '管理员', null, '1', '/avatar1.jpg');
INSERT INTO `users` VALUES ('3', 'huge', 'scrypt:32768:8:1$CshMbmk5w5JgtViW$801c8658a2ad5a0905276b6c6ebd91e24454f27f1205abed3850c742531c1dabb2e7475d0253511a1cadbd4b323defec46337b0555a57fecc488ce60b46a77e4', '胡歌', '学生', null, '1', '/static/images/avatars/avatar_3_1743519922.jpg');
INSERT INTO `users` VALUES ('4', '教师', 'scrypt:32768:8:1$9FhztB1BLNjYmpCT$fe8bc7220e4bba822778ee10f0e85cda2c4fa22698ae9dfd6ba70fbb595658cc7ac65659268b38e0e981e82962c3c6ed7d5dc9175ac0c7b31b96ab3e316610b1', '李老师', '教师', null, '1', '/avatar2.jpg');
INSERT INTO `users` VALUES ('5', '教师2', 'scrypt:32768:8:1$a9T8ra2K8rCvW65M$e9ddf317acc365d2415c645b9c3c49b094a5b324b3963cc1eb616a0bc739028ebfe1fb865f12a86712f10c8991d4debf11da4ef59e957096ba5cf9cae36b44e7', '教师2real', '教师', null, '1', '/static/images/avatars/avatar_5_1744729867.jpg');
INSERT INTO `users` VALUES ('6', '学生2', 'scrypt:32768:8:1$kBTh13PAhzzo1nmy$6e5c5ddc285d3df20a243577715079c223c6c8984f514b937c0a65c74bbde36e9e7c66defbaa37ee17b59f34cce0a247331894a6d281754a84b268597501a623', '学生2real', '学生', null, '1', '/static/images/avatars/avatar_6_1744771549.jpg');
INSERT INTO `users` VALUES ('7', '学生3', 'scrypt:32768:8:1$l54QO0qzFbiEPg2t$5553e4776a9966686d246ebc6be38a938bde0dfd8d4d70feffc533cc0a846bb0445867f614143d3440285c7fa67fa2e1534c501dbe550fd81e0acf8daaa658a4', '学生3real', '学生', 'mom@qq.com', '1', '/static/images/avatars/avatar_7_1744890788.jpg');

# 更新数据库表结构
# 方案1：如果check_in_type是枚举类型，需要修改枚举值
ALTER TABLE attendance_records MODIFY COLUMN check_in_type ENUM('正常', '迟到', '异常', '识别尝试') NOT NULL;

# 方案2：如果是字符串类型，但长度不够，可以增加长度
ALTER TABLE attendance_records MODIFY COLUMN check_in_type VARCHAR(20) NOT NULL; 
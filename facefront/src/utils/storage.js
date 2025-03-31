// 安全地存储对象到localStorage
export function safeSetItem(key, value) {
  try {
    const jsonValue = JSON.stringify(value);
    localStorage.setItem(key, jsonValue);
  } catch (e) {
    console.error('存储数据失败:', e);
  }
}

// 安全地从localStorage获取对象
export function safeGetItem(key, defaultValue = null) {
  try {
    const value = localStorage.getItem(key);
    if (value === null) return defaultValue;
    return JSON.parse(value);
  } catch (e) {
    console.error('读取数据失败:', e);
    return defaultValue;
  }
} 
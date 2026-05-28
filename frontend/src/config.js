// 判断当前运行模式
const isDev = import.meta.env.DEV

// 后端地址配置
// 开发模式：本地后端 8000 端口
// 生产模式：前后端同域部署，使用空字符串（相对路径）
export const API_URL = isDev ? 'http://localhost:8000' : ''
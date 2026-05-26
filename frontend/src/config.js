// 判断当前运行模式
// 当你在本地执行 npm run dev 时，import.meta.env.DEV 为 true
// 当你执行 npm run build 并部署到 Netlify 后，import.meta.env.PROD 为 true
const isDev = import.meta.env.DEV

// 后端地址配置
export const API_URL = isDev
  ? 'http://localhost:8000'   // 本地开发模式 (npm run dev) 使用本地后端
  : 'https://secure-achievement-production-a328.up.railway.app'  // 生产模式 (npm run build) 使用云端后端
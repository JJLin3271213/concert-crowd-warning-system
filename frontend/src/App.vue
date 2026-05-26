<template>
  <router-view />
</template>

<style>
/* === 全局设计系统 === */
:root {
  --bg-deep: #0a0a1a;
  --bg-mid: #12122a;
  --bg-card: rgba(255,255,255,0.06);
  --glass: rgba(255,255,255,0.08);
  --glass-strong: rgba(255,255,255,0.14);
  --border-glass: rgba(255,255,255,0.10);
  --text-primary: #e8e8f0;
  --text-secondary: #9898b8;
  --accent: #7c5cfc;
  --accent-glow: rgba(124,92,252,0.3);
  --green: #22d67a;
  --yellow: #f5c842;
  --orange: #ff8c42;
  --red: #ff4d5a;
  --blue: #42a5f5;
  --radius: 18px;
  --radius-sm: 10px;
  --shadow-card: 0 4px 30px rgba(0,0,0,0.3);
  --shadow-glow: 0 0 30px var(--accent-glow);
  --transition: 0.3s cubic-bezier(0.4,0,0.2,1);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: var(--bg-deep);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}

/* 动态星空背景 */
body::before {
  content: '';
  position: fixed; inset: 0;
  background:
    radial-gradient(ellipse at 20% 20%, rgba(124,92,252,0.12) 0%, transparent 50%),
    radial-gradient(ellipse at 70% 60%, rgba(66,165,245,0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 40% 80%, rgba(255,77,90,0.06) 0%, transparent 50%),
    var(--bg-deep);
  z-index: -2;
}

body::after {
  content: '';
  position: fixed; inset: 0;
  background-image:
    radial-gradient(1px 1px at 10% 15%, rgba(255,255,255,0.4), transparent),
    radial-gradient(1px 1px at 25% 45%, rgba(255,255,255,0.3), transparent),
    radial-gradient(1.5px 1.5px at 40% 25%, rgba(255,255,255,0.5), transparent),
    radial-gradient(1px 1px at 55% 65%, rgba(255,255,255,0.3), transparent),
    radial-gradient(1.5px 1.5px at 70% 35%, rgba(255,255,255,0.4), transparent),
    radial-gradient(1px 1px at 85% 55%, rgba(255,255,255,0.3), transparent),
    radial-gradient(1px 1px at 15% 75%, rgba(255,255,255,0.2), transparent),
    radial-gradient(1.5px 1.5px at 60% 85%, rgba(255,255,255,0.4), transparent);
  z-index: -1;
  animation: twinkle 6s ease-in-out infinite alternate;
}

@keyframes twinkle {
  0% { opacity: 0.5; }
  100% { opacity: 1; }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

@keyframes pulse-warn {
  0%, 100% { box-shadow: 0 0 5px rgba(255,77,90,0.3); }
  50% { box-shadow: 0 0 25px rgba(255,77,90,0.7); }
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* 玻璃拟态卡片 */
.glass-card {
  background: var(--glass);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius);
  box-shadow: var(--shadow-card);
  transition: all var(--transition);
}
.glass-card:hover {
  background: var(--glass-strong);
  transform: translateY(-3px);
  box-shadow: var(--shadow-glow), var(--shadow-card);
}

/* 滚动条 */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 3px; }

/* Element Plus 暗色覆写 */
.el-select .el-input__wrapper,
.el-input__wrapper {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 10px !important;
  box-shadow: none !important;
}
.el-select .el-input__inner,
.el-input__inner {
  color: var(--text-primary) !important;
}
.el-select-dropdown,
.el-dialog {
  background: #1a1a35 !important;
  border: 1px solid var(--border-glass) !important;
}
.el-select-dropdown__item {
  color: var(--text-secondary) !important;
}
.el-select-dropdown__item:hover,
.el-select-dropdown__item.selected {
  background: rgba(124,92,252,0.2) !important;
  color: #fff !important;
}
.el-tabs__item {
  color: var(--text-secondary) !important;
}
.el-tabs__item.is-active {
  color: var(--accent) !important;
}
.el-tabs__active-bar {
  background: var(--accent) !important;
}
.el-table {
  --el-table-bg-color: transparent !important;
  --el-table-tr-bg-color: transparent !important;
  --el-table-header-bg-color: rgba(255,255,255,0.04) !important;
  --el-table-border-color: rgba(255,255,255,0.06) !important;
  --el-table-text-color: var(--text-primary) !important;
  --el-table-header-text-color: var(--text-secondary) !important;
}
.el-table th.el-table__cell { background: rgba(255,255,255,0.04) !important; }
.el-button--primary { --el-button-bg-color: var(--accent); --el-button-border-color: var(--accent); }
.el-dialog { border-radius: 18px !important; }
.el-dialog__header { background: linear-gradient(135deg, rgba(124,92,252,0.2), rgba(66,165,245,0.1)); border-radius: 18px 18px 0 0; padding: 18px 24px; }

@media (max-width: 768px) {
  :root { --radius: 14px; --radius-sm: 8px; }
}
</style>

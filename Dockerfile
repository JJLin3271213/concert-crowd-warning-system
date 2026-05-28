# ===== 阶段1：构建前端 =====
FROM node:22-alpine AS frontend-build

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ===== 阶段2：Python 后端 =====
FROM python:3.11-slim

WORKDIR /app

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY *.py ./

# 复制前端构建产物
COPY --from=frontend-build /frontend/dist ./frontend/dist

# 复制数据库文件（含预置数据）
COPY concert.db ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
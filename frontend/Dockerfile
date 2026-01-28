# 前端 Dockerfile
# 使用多阶段构建：构建阶段 + 运行阶段

# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装所有依赖（包括开发依赖）
RUN npm ci

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# 开发阶段（用于开发模式）
FROM node:18-alpine AS dev

WORKDIR /app

COPY package*.json ./
RUN npm ci

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# 运行阶段 - 使用 nginx 提供静态文件服务
FROM nginx:alpine AS production

# 复制构建产物到 nginx 目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]

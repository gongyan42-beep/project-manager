FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# 复制项目文件
COPY . .

# 设置环境变量
ENV PORT=3007
ENV PROJECTS_DIR=/www/wwwroot

# 暴露端口
EXPOSE 3007

# 启动命令
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:3007", "app:app"]

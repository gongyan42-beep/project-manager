#!/bin/bash

PROJECT_NAME="project-manager"
DEPLOY_DIR="deploy"

echo "📦 开始打包 ${PROJECT_NAME}..."
echo ""

# 创建部署目录
mkdir -p ${DEPLOY_DIR}

# 清理临时文件
echo "🧹 清理临时文件..."
rm -rf venv/
rm -rf __pycache__/
rm -rf modules/__pycache__/
rm -rf *.pyc
rm -rf .DS_Store
rm -rf ${DEPLOY_DIR}/*.tar.gz

# 创建 .dockerignore
cat > .dockerignore <<EOF
venv
__pycache__
*.pyc
.DS_Store
.git
deploy/
EOF

# 打包
echo "📦 打包项目文件..."
tar -czf ${DEPLOY_DIR}/${PROJECT_NAME}.tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='deploy/*.tar.gz' \
    .

echo ""
echo "✅ 打包完成！"
echo "📍 部署包位置：${DEPLOY_DIR}/${PROJECT_NAME}.tar.gz"
echo ""
echo "下一步："
echo "1. 上传到服务器：scp -i ~/.ssh/baota_server_key ${DEPLOY_DIR}/${PROJECT_NAME}.tar.gz root@118.25.13.91:/www/wwwroot/"
echo "2. 查看部署说明：cat deploy/宝塔部署步骤.md"

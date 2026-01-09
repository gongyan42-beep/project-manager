#!/bin/bash

echo "🚀 正在启动【项目管理器】..."
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 首次运行，正在安装依赖..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "⚠️  配置文件不存在"
    exit 1
fi

# 启动服务
echo "✅ 启动成功！"
echo "📍 访问地址：http://localhost:5003"
echo "💡 按 Ctrl+C 停止服务"
echo ""

# 自动打开浏览器
sleep 2
open http://localhost:5003 2>/dev/null || true

# 运行应用
python app.py

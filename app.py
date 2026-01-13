"""
Flask 应用主文件
"""
from flask import Flask, render_template, jsonify, request
import os
from pathlib import Path
from dotenv import load_dotenv
from modules.project_scanner import ProjectScanner, ProjectManager

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 项目配置
PROJECTS_DIR = os.getenv('PROJECTS_DIR', '/Users/gusuping/code')
PORT = int(os.getenv('PORT', 5003))

# 初始化扫描器和管理器
scanner = ProjectScanner(PROJECTS_DIR)
manager = ProjectManager()


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/projects', methods=['GET'])
def get_projects():
    """获取所有项目"""
    try:
        projects = scanner.scan_projects()

        # 检查每个项目的运行状态
        for project in projects:
            if project['port']:
                is_running = scanner.check_project_status(project['port'])
                project['status'] = 'running' if is_running else 'stopped'

        return jsonify({
            'success': True,
            'projects': projects
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/projects/start', methods=['POST'])
def start_project():
    """启动项目"""
    try:
        data = request.json
        project_path = data.get('path')

        if not project_path:
            return jsonify({'success': False, 'message': '缺少项目路径'}), 400

        # 安全检查：确保路径在允许的目录内
        allowed_paths = ['/Users/gusuping/', '/www/wwwroot/']
        if not any(project_path.startswith(p) for p in allowed_paths):
            return jsonify({'success': False, 'message': '无效的项目路径'}), 400

        result = manager.start_project(project_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': f'启动失败: {str(e)}'}), 500


@app.route('/api/projects/stop', methods=['POST'])
def stop_project():
    """停止项目"""
    try:
        data = request.json
        port = data.get('port')

        if not port:
            return jsonify({'success': False, 'message': '缺少端口号'}), 400

        # 安全检查：端口必须是数字
        try:
            port_num = int(port)
            if port_num < 1 or port_num > 65535:
                return jsonify({'success': False, 'message': '无效的端口号'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': '端口号必须是数字'}), 400

        result = manager.stop_project(port)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': f'停止失败: {str(e)}'}), 500


@app.route('/api/projects/<project_name>', methods=['GET'])
def get_project_detail(project_name):
    """获取项目详情"""
    try:
        # 安全检查：防止路径遍历攻击
        if '..' in project_name or '/' in project_name:
            return jsonify({
                'success': False,
                'message': '无效的项目名称'
            }), 400

        project_path = Path(PROJECTS_DIR) / project_name
        readme_path = project_path / 'README.md'

        readme_content = '# 无 README 文件'
        try:
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
        except (PermissionError, OSError):
            readme_content = '# 无法读取 README 文件（权限不足）'

        return jsonify({
            'success': True,
            'readme': readme_content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/projects/open-terminal', methods=['POST'])
def open_terminal():
    """在终端中打开项目目录（仅本地可用）"""
    import subprocess
    import platform

    try:
        data = request.json
        project_path = data.get('path')

        if not project_path:
            return jsonify({'success': False, 'message': '缺少项目路径'}), 400

        # 安全检查：确保路径在允许的目录内，且不包含危险字符
        allowed_paths = ['/Users/gusuping/', '/www/wwwroot/']
        if not any(project_path.startswith(p) for p in allowed_paths):
            return jsonify({'success': False, 'message': '无效的项目路径'}), 400
        if "'" in project_path or '"' in project_path or ';' in project_path:
            return jsonify({'success': False, 'message': '路径包含非法字符'}), 400

        # 仅在 macOS 本地环境下支持打开终端
        if platform.system() != 'Darwin':
            return jsonify({
                'success': False,
                'message': '此功能仅在本地 Mac 环境可用，线上版本请直接 SSH 到服务器操作'
            }), 400

        # 使用 AppleScript 打开新的终端窗口并进入项目目录
        script = f'''
        tell application "Terminal"
            activate
            do script "cd '{project_path}' && clear && echo '🚀 已进入项目: {project_path}' && echo '' && echo '现在你可以输入 claude 开始对话' && echo ''"
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True, timeout=10)

        return jsonify({
            'success': True,
            'message': f'已在终端打开: {project_path}'
        })
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'message': '打开终端超时'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'打开终端失败: {str(e)}'
        }), 500


if __name__ == '__main__':
    print(f"""
╔═══════════════════════════════════════╗
║   🚀 项目管理器已启动                  ║
╠═══════════════════════════════════════╣
║   📍 访问地址: http://localhost:{PORT}  ║
║   📁 项目目录: {PROJECTS_DIR}
║   💡 按 Ctrl+C 停止服务                ║
╚═══════════════════════════════════════╝
    """)

    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=True
    )

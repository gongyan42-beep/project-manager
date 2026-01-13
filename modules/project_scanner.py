"""
项目扫描和管理模块
"""
import os
import json
import subprocess
from pathlib import Path

class ProjectScanner:
    def __init__(self, projects_dir):
        self.projects_dir = Path(projects_dir)

    def scan_projects(self):
        """扫描所有项目"""
        projects = []

        # 根据配置的目录动态设置扫描位置
        scan_locations = [self.projects_dir]

        # 本地 Mac 环境额外扫描用户主目录
        if str(self.projects_dir).startswith('/Users/gusuping'):
            scan_locations.append(Path('/Users/gusuping'))

        # 服务器环境只扫描 /www/wwwroot
        # （不需要额外添加，因为 self.projects_dir 就是它）

        for location in scan_locations:
            if not location.exists():
                continue

            try:
                items = list(location.iterdir())
            except PermissionError:
                # 跳过没有权限访问的目录
                continue

            for item in items:
                try:
                    # 跳过隐藏文件、非目录、文档文件
                    if item.name.startswith('.'):
                        continue
                    if not item.is_dir():
                        continue
                    # macOS 系统目录和受保护目录（绝对不扫描）
                    if item.name in ['Desktop', 'Downloads', 'Documents', 'Library',
                                    'Applications', 'Movies', 'Music', 'Pictures',
                                    'Public', 'Sites', '.Trash', '.cache', '.npm',
                                    '.ssh', '.config', 'venv', 'node_modules',
                                    'Parallels', 'Creative Cloud Files', 'OneDrive']:
                        continue

                    # 检查是否是开发项目（有 README 或 package.json 或 requirements.txt）
                    if not self._is_dev_project(item):
                        continue

                    project_info = self._get_project_info(item)
                    if project_info:
                        # 避免重复
                        if not any(p['path'] == project_info['path'] for p in projects):
                            projects.append(project_info)
                except (PermissionError, OSError):
                    # 跳过任何权限问题的目录
                    continue

        return sorted(projects, key=lambda x: x['name'])

    def _is_dev_project(self, path):
        """判断是否是开发项目"""
        try:
            indicators = [
                'README.md', 'readme.md',
                'package.json',
                'requirements.txt',
                'Dockerfile',
                'app.py', 'main.py', 'server.js',
                '.git'
            ]
            return any((path / indicator).exists() for indicator in indicators)
        except (PermissionError, OSError):
            return False

    def _get_project_info(self, project_path):
        """获取项目信息"""
        try:
            project_name = project_path.name
            readme_path = project_path / 'README.md'
            env_path = project_path / '.env'
            start_script = project_path / 'start.sh'

            # 获取最近修改时间
            try:
                last_modified = os.path.getmtime(project_path)
            except:
                last_modified = 0

            # 检测文件是否存在（可能触发权限错误）
            try:
                has_start = start_script.exists()
            except:
                has_start = False

            # 读取基本信息
            info = {
                'name': project_name,
                'chinese_name': self._get_chinese_name(project_name),
                'path': str(project_path),
                'has_start_script': has_start,
                'description': '无描述',
                'port': None,
                'tech_stack': [],
                'status': 'stopped',
                'category': self._detect_category(project_path, project_name),
                'last_modified': last_modified,
                'online_url': self._get_online_url(project_name)
            }

            # 从 README 获取描述
            try:
                if readme_path.exists():
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if '这是什么' in line and i + 1 < len(lines):
                                info['description'] = lines[i + 1].strip()
                                break
                            if not info['description'] or info['description'] == '无描述':
                                if line.strip() and not line.startswith('#'):
                                    info['description'] = line.strip()[:100]
                                    break
            except:
                pass

            # 从 .env 获取端口
            try:
                if env_path.exists():
                    with open(env_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('PORT='):
                                info['port'] = line.split('=')[1].strip()
                                break
            except:
                pass

            # 检测技术栈
            try:
                if (project_path / 'requirements.txt').exists():
                    info['tech_stack'].append('Python')
                if (project_path / 'package.json').exists():
                    info['tech_stack'].append('Node.js')
                if (project_path / 'app.py').exists():
                    info['tech_stack'].append('Flask')
                if (project_path / 'Dockerfile').exists():
                    info['tech_stack'].append('Docker')
            except:
                pass

            return info
        except (PermissionError, OSError):
            return None

    def _get_chinese_name(self, project_name):
        """获取项目中文名"""
        name_map = {
            'douyin-to-notion': '抖音同步到Notion',
            'feishu-drive-sync': '飞书云文档同步',
            'feishu-weekly-report': '飞书周报评价系统',
            'project-manager': '项目管理器',
            'n8n': 'N8N自动化工作流',
            'ai-image-gen-template': 'AI图片生成模板',
            'ai-multi-sender-extension': 'AI多平台发送插件',
            'aihuantu-project': 'AI换图项目',
            'psychology-test': '心理测试系统',
            'weather-app': '天气应用',
            'notion-sync': 'Notion同步工具',
            'video-downloader': '视频下载器',
            'data-analyzer': '数据分析工具',
            'api-gateway': 'API网关',
            'chatbot': '聊天机器人',
            'website-monitor': '网站监控工具',
            'image-compressor': '图片压缩工具',
            'pdf-converter': 'PDF转换器',
            'email-sender': '邮件发送工具',
            'file-sync': '文件同步工具',
            'taobao-feishu-sync': '淘宝飞书同步',
            'xiaohongshu-feishu-sync': '小红书飞书同步',
            'xhs-monitor': '小红书监控',
            'video-sync-project': '视频同步项目',
            'yuanshengceshi': '原生测试',
            'talent-assessment': '人才测评系统',
            'claude-code-showcase': 'Claude Code 展示',
            'career-assessment': '大学生就业能力测评',
            'youtube-to-notion': 'YouTube字幕同步到Notion',
        }
        return name_map.get(project_name, project_name)

    def _get_online_url(self, project_name):
        """获取项目的线上网站地址（根据腾讯云DNS配置）"""
        # 域名映射表：项目名 -> 线上域名
        # 【重要】每次部署新项目到线上后，必须更新此映射表！
        url_map = {
            # 数据同步类
            'taobao-feishu-sync': 'https://taobao.longgonghuohuo.com',
            'feishu-drive-sync': 'https://feishu.longgonghuohuo.com',
            'feishu-weekly-report': 'https://feishu.longgonghuohuo.com',
            'xhs-monitor': 'https://xfollow.longgonghuohuo.com',

            # 测试/问卷类
            'psychology-test': 'https://xinliceshi.longgonghuohuo.com',
            'yuanshengceshi': 'https://yuanshengceshi.longgonghuohuo.com',
            'career-assessment': 'https://career.longgonghuohuo.com',

            # 工具类
            'aihuantu-project': 'https://aihuantu.longgonghuohuo.com',
            'claude-code-showcase': 'https://showcase.longgonghuohuo.com',
            'project-manager': 'https://pm.longgonghuohuo.com',

            # 其他
            'ryhd': 'https://ryhd.longgonghuohuo.com',
            'youtube-to-notion': 'https://youtube.longgonghuohuo.com',

            # 管理工具
            'kpi-design-tool': 'https://kpi.longgonghuohuo.com',
        }
        return url_map.get(project_name)

    def _detect_category(self, project_path, project_name):
        """检测项目类别"""
        try:
            name_lower = project_name.lower()

            # 根据名称关键词判断
            if 'sync' in name_lower or 'to-notion' in name_lower or 'feishu' in name_lower:
                return '数据同步'
            elif 'monitor' in name_lower or 'watch' in name_lower:
                return '监控工具'
            elif 'test' in name_lower or 'psychology' in name_lower:
                return '测试/问卷'
            elif 'manager' in name_lower or 'dashboard' in name_lower:
                return '管理工具'
            elif 'api' in name_lower:
                return 'API服务'
            elif 'bot' in name_lower:
                return '机器人'
            elif 'n8n' in name_lower:
                return '自动化工作流'

            # 根据文件特征判断（加保护）
            try:
                if (project_path / 'templates').exists() or (project_path / 'static').exists():
                    return '网站应用'
                elif (project_path / 'package.json').exists():
                    try:
                        with open(project_path / 'package.json', 'r') as f:
                            pkg = json.load(f)
                            if 'dependencies' in pkg:
                                if 'react' in pkg['dependencies'] or 'next' in pkg['dependencies']:
                                    return '前端应用'
                    except:
                        pass
            except:
                pass

            return '其他'
        except:
            return '其他'

    def check_project_status(self, port):
        """检查项目是否在运行"""
        if not port:
            return False

        try:
            # 使用 lsof 检查端口是否被占用
            result = subprocess.run(
                ['lsof', '-i', f':{port}', '-sTCP:LISTEN'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return bool(result.stdout.strip())
        except:
            return False


class ProjectManager:
    def __init__(self):
        self.running_processes = {}

    def start_project(self, project_path):
        """启动项目"""
        project_path = Path(project_path)
        start_script = project_path / 'start.sh'

        if not start_script.exists():
            return {'success': False, 'message': '项目没有 start.sh 文件'}

        try:
            # 使用 subprocess 在后台启动项目
            process = subprocess.Popen(
                ['bash', str(start_script)],
                cwd=str(project_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )

            self.running_processes[str(project_path)] = process

            return {
                'success': True,
                'message': f'项目启动中... PID: {process.pid}',
                'pid': process.pid
            }
        except Exception as e:
            return {'success': False, 'message': f'启动失败: {str(e)}'}

    def stop_project(self, port):
        """停止项目"""
        if not port:
            return {'success': False, 'message': '未知端口'}

        try:
            # 查找占用端口的进程并终止
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(['kill', pid], timeout=2)

                return {'success': True, 'message': f'已停止端口 {port} 的进程'}
            else:
                return {'success': False, 'message': '没有找到运行中的进程'}
        except Exception as e:
            return {'success': False, 'message': f'停止失败: {str(e)}'}

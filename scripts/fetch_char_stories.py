# -*- coding: utf-8 -*-
"""批量抓取米游社Wiki角色故事，添加到角色文件中"""
import sys, os, re, json, time, random, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

API_URL = 'https://act-api-takumi-static.mihoyo.com/common/blackboard/sr_wiki/v1/content/info?app_sn=sr_wiki&content_id={cid}'
CHAR_DIR = 'character'
PROGRESS_FILE = '.tmp_build/story_progress.json'

def clean_html(text):
    """清理HTML标签，保留文本"""
    text = re.sub(r'<i[^>]*>', '', text)
    text = re.sub(r'</i>', '', text)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
    return text.strip()

def fetch_story(cid):
    """从Wiki接口抓取角色故事"""
    url = API_URL.format(cid=cid)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        data = json.loads(resp.read().decode('utf-8'))
        if data.get('retcode') != 0:
            return None, f"API错误: {data.get('message')}"
        
        rpg = data['data']['content'].get('rpg_new_tmp_content', {})
        modules = rpg.get('modules', [])
        
        for m in modules:
            if m.get('name') == '角色故事':
                components = m.get('components', [])
                for c in components:
                    if c.get('componentId') == 'character_story':
                        data_str = c.get('data', '')
                        if not data_str:
                            return None, "角色故事data为空"
                        story_data = json.loads(data_str)
                        return story_data, None
                return None, "未找到character_story组件"
        return None, "未找到角色故事module"
    except Exception as e:
        return None, str(e)

def format_story_md(story_data):
    """将角色故事数据格式化为Markdown"""
    lines = []
    detail = story_data.get('detail', '')
    if detail:
        lines.append(clean_html(detail))
        lines.append('')
    
    story_list = story_data.get('list', [])
    for item in story_list:
        tab_name = item.get('tabName', '')
        append = item.get('append', '')
        desc = item.get('desc', '')
        
        title = tab_name
        if append:
            title += f' {append}'
        lines.append(f'### {title}')
        lines.append('')
        lines.append(clean_html(desc))
        lines.append('')
    
    return '\n'.join(lines)

def add_story_to_file(fp, story_md):
    """将角色故事添加到角色文件中（基本信息之后）"""
    with open(fp, encoding='utf-8') as f:
        txt = f.read()
    
    # 检查是否已有角色故事章节
    if '## 角色故事' in txt:
        # 替换已有章节
        pattern = r'(## 角色故事\n).*?(?=## 基础属性|## 晋阶材料|## 技能材料)'
        txt = re.sub(pattern, r'\1' + story_md + '\n', txt, flags=re.DOTALL)
    else:
        # 在基本信息之后插入
        pattern = r'(## 基本信息\n.*?)(?=\n## 基础属性)'
        if re.search(pattern, txt, re.DOTALL):
            txt = re.sub(pattern, r'\1\n\n## 角色故事\n' + story_md + '\n', txt, flags=re.DOTALL)
        else:
            # 找不到插入点，追加到文件末尾
            txt += '\n\n## 角色故事\n' + story_md + '\n'
    
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(txt)

# 加载进度
progress = {}
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, encoding='utf-8') as f:
        progress = json.load(f)

# 收集所有角色
chars = []
for root, dirs, fs in os.walk(CHAR_DIR):
    for f in fs:
        if not f.endswith('.md') or f == '角色.md':
            continue
        fp = os.path.join(root, f)
        txt = open(fp, encoding='utf-8').read()
        m = re.search(r'bbs\.mihoyo\.com/sr/wiki/content/(\d+)', txt)
        if m:
            cid = m.group(1)
            name = f.replace('.md', '')
            chars.append((name, cid, fp))

print(f"共 {len(chars)} 个角色待处理")
success = 0
failed = []
skipped = 0

for i, (name, cid, fp) in enumerate(chars):
    if cid in progress and progress[cid].get('status') == 'success':
        skipped += 1
        continue
    
    print(f"[{i+1}/{len(chars)}] {name} (cid={cid})...", end=' ')
    story_data, err = fetch_story(cid)
    
    if err:
        print(f"失败: {err}")
        failed.append((name, cid, err))
        progress[cid] = {'status': 'failed', 'error': err, 'name': name}
    else:
        story_md = format_story_md(story_data)
        add_story_to_file(fp, story_md)
        print(f"成功 ({len(story_data.get('list', []))}章)")
        success += 1
        progress[cid] = {'status': 'success', 'name': name, 'chapters': len(story_data.get('list', []))}
    
    # 保存进度
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)
    
    # 控制请求频率
    if i < len(chars) - 1:
        time.sleep(random.uniform(1.5, 3.0))

print(f"\n=== 完成 ===")
print(f"成功: {success}")
print(f"跳过(已完成): {skipped}")
print(f"失败: {len(failed)}")
for name, cid, err in failed:
    print(f"  {name} (cid={cid}): {err}")

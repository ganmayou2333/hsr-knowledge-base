# -*- coding: utf-8 -*-
"""探测 hsr.nanoka.cc 数据接口，寻找模拟宇宙祝福/奇物/事件数据"""
import urllib.request, re

def probe(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        r = urllib.request.urlopen(req, timeout=15)
        data = r.read()
        ct = r.headers.get('Content-Type', '')
        print('[%s] %s | %d bytes | %s' % (url, r.status, len(data), ct))
        return data
    except Exception as e:
        print('[%s] FAIL %s' % (url, e))
        return None

html = probe('https://hsr.nanoka.cc/')
if html:
    t = html.decode('utf-8', errors='ignore')
    print('--- 页面长度:', len(t))
    # 找 script/href 资源
    for m in re.findall(r'(?:src|href)="([^"]+)"', t)[:30]:
        print('资源:', m)
    # 找页面路径线索（路由）
    for m in re.findall(r'["\']/(?:blessing|curio|rogue|simulat|event|奇物|祝福|模拟)[a-zA-Z0-9_/.-]*["\']', t, re.I)[:30]:
        print('路由线索:', m)

# 探测常见接口
print('\n=== 常见接口探测 ===')
for u in ['https://hsr.nanoka.cc/blessing',
          'https://hsr.nanoka.cc/curio',
          'https://hsr.nanoka.cc/rogue',
          'https://hsr.nanoka.cc/api/blessings',
          'https://hsr.nanoka.cc/_nuxt/' ]:
    probe(u)

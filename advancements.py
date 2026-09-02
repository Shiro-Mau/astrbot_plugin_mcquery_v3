# -*- coding: utf-8 -*-
"""Java 版进度查询：中文进度名 -> 数据 + 出图"""
import json, os
from .render_adv import render_adv

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, 'mcquery_v3', 'Accom_Database', 'advancements.json')

_advs = None
_key2name = None


def _load():
    global _advs, _key2name
    if _advs is None:
        with open(DB, encoding='utf-8') as f:
            _advs = json.load(f)
        _key2name = {a['key']: a['title_zh'] for a in _advs}


def _with_upstream(a):
    d = dict(a)
    d['upstream_name'] = _key2name.get(a['upstream'], '')
    return d


def query_adv(name):
    """输入中文进度名，返回进度数据 dict 或 None。
    返回: dict 含 key/title_zh/title_en/desc/require/icon/bg/category/upstream/upstream_name
    模糊匹配多个时返回 {'ambiguous': [名称, ...]}
    """
    _load()
    if not name:
        return None
    for a in _advs:
        if a['title_zh'] == name:
            return _with_upstream(a)
    matches = [a for a in _advs if name in a['title_zh'] or name.lower() in a['title_en'].lower()]
    if len(matches) == 1:
        return _with_upstream(matches[0])
    if matches:
        return {'ambiguous': [a['title_zh'] for a in matches]}
    return None


if __name__ == '__main__':
    import sys
    os.makedirs('render_test', exist_ok=True)
    cases = ['石器时代', '末地', '成双成对'] if len(sys.argv) < 2 else [sys.argv[1]]
    for cn in cases:
        r = query_adv(cn)
        if not r:
            print(f'✗ {cn}: 查不到')
            continue
        if 'ambiguous' in r:
            print(f'~ {cn}: 多个匹配 {r["ambiguous"]}')
            continue
        img = render_adv(r, r.get('upstream_name', ''))
        p = f'render_test/adv_query_{cn}.png'
        img.save(p)
        print(f'✓ {cn} -> {p} {img.size}')

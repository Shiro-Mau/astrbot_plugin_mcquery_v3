# -*- coding: utf-8 -*-
"""物品描述查询：中文名 -> 描述数据（变体走 variant_map 复用父页面）"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, 'mcquery_v3', 'Database')

_items = None
_vm = None
_vim = None


def _load():
    global _items, _vm, _vim
    if _items is None:
        with open(os.path.join(DB, 'items.json'), encoding='utf-8') as f:
            _items = json.load(f)
    if _vm is None:
        with open(os.path.join(DB, 'variant_map.json'), encoding='utf-8') as f:
            _vm = json.load(f)
    if _vim is None:
        with open(os.path.join(DB, 'variant_icon_map.json'), encoding='utf-8') as f:
            _vim = json.load(f)


def normalize_candidates(name):
    """生成查询候选：原样 + 去括号变体，让目录带括号名也能命中。"""
    cands = [name]
    variants = [
        name.replace('（', '').replace('）', ''),
        name.replace('(', '').replace(')', ''),
        name.replace('（', '').replace('）', '').replace('(', '').replace(')', ''),
        name.replace(' ', ''),
    ]
    # 去最外层括号（保留中间）：X（Y）-> XY，兼容双层括号
    for op, cl in (('（', '）'), ('(', ')')):
        first = name.find(op)
        last = name.rfind(cl)
        if first != -1 and last > first:
            variants.append(name[:first] + name[first + 1:last] + name[last + 1:])
    for v in variants:
        if v and v != name and v not in cands:
            cands.append(v)
    return cands


def query_desc(name):
    """输入中文物品名，返回描述数据 dict 或 None。

    返回: {'title': 标题名, 'en': 英文名, 'icon': 图标名, 'sections': [(小标题, 正文), ...]}
    - 命中 items.json：title 即该物品名，描述用自身
    - 命中 variant_map.json：title 用父页面名，描述复用父页面
    - 都没命中：返回 None
    """
    _load()
    if not name:
        return None
    for c in normalize_candidates(name):
        if c in _items:
            d = _items[c]
            return {'title': c, 'en': d.get('en', ''), 'icon': d.get('icon', ''),
                    'lead': d.get('lead', ''), 'sections': d.get('sections', [])}
        if c in _vm:
            parent = _vm[c]
            if parent in _items:
                d = _items[parent]
                icon = _vim.get(c, d.get('icon', ''))
                return {'title': parent, 'en': d.get('en', ''), 'icon': icon,
                        'lead': d.get('lead', ''), 'sections': d.get('sections', [])}
    return None


if __name__ == '__main__':
    from desc_render import render_desc
    os.makedirs('render_test', exist_ok=True)

    cases = [
        '苹果',          # items 直接命中
        '铁门',          # items 直接命中（独立父页面）
        '云杉木门',      # variant -> 木门
        '铁头盔',        # variant -> 盔甲
        '红色羊毛',      # variant -> 羊毛
        '斑驳的铜块',    # variant -> 铜块
    ]
    for name in cases:
        r = query_desc(name)
        if not r:
            print(f'  ✗ {name}: 查不到')
            continue
        img = render_desc(r['title'], r['en'], r['icon'], r['sections'])
        p = f"render_test/mq_desc_{name}.png"
        img.save(p)
        print(f"  ✓ {name} -> title={r['title']} icon={r['icon']} sections={len(r['sections'])} -> {p}")
    print('OK')

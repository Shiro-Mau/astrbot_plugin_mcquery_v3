# -*- coding: utf-8 -*-
"""mcquery_v3 数据自检脚本（四合一审计）。

用法（插件目录内）:
    python test_icons.py

检查四类问题，任何一类有缺口都会列出并返回退出码 1：
  1. 图标覆盖    —— 每条配方引用的材料名，load_icon 必须能解析出图标
  2. 描述覆盖    —— 每个配方条目（中文名）必须能查到描述（items / variant_map）
  3. 变体完整性  —— 已知 16 色家族（羊毛楼梯/混凝土/染色玻璃…）不能缺色
  4. 无序标记    —— 已知无序配方（烟火之星）必须标记 shapeless，防止再被形状化

数据更新后跑一遍，三类问题一次拦住。
"""
import sys
import os

# 支持插件目录内直接 `python test_icons.py`
_HERE = os.path.dirname(os.path.abspath(__file__))
_PLUGINS = os.path.dirname(_HERE)
if _PLUGINS not in sys.path:
    sys.path.insert(0, _PLUGINS)

from astrbot_plugin_mcquery_v3.render_mq import load_icon  # noqa: E402
from astrbot_plugin_mcquery_v3.desc_query import query_desc, _load  # noqa: E402

BASE = os.path.join(_HERE, 'mcquery_v3')
PRESC = os.path.join(BASE, 'Prescription')
FILES = [('craft', 'crafting.json'), ('smelt', 'smelting.json'), ('smith', 'smithing.json'),
         ('stonecut', 'stonecutting.json'), ('brew', 'brewing.json')]

# 描述覆盖允许缺失的条目（彩蛋等，查询入口会单独处理）
DESC_ALLOW_MISS = {'莎莎'}

# 已知 16 色家族：这些后缀在游戏里必须是 16 色齐全
MUST_16_COLORS = ['白色', '橙色', '品红色', '淡蓝色', '黄色', '黄绿色', '粉红色',
                  '灰色', '淡灰色', '青色', '紫色', '蓝色', '棕色', '绿色', '红色', '黑色']
MUST_16_FAMILIES = ['羊毛', '羊毛楼梯', '羊毛台阶', '混凝土', '混凝土粉末',
                    '染色玻璃', '染色玻璃板', '陶瓦', '地毯', '床', '旗帜', '挽具',
                    '坐垫', '潜影盒', '染料', '蜡烛']

# 已知无序配方：这些条目在游戏里全部是无序，数据必须带 shapeless 标记
KNOWN_SHAPELESS = {'烟火之星'}


def load_prescriptions():
    import json
    data = {}
    for kind, fn in FILES:
        with open(os.path.join(PRESC, fn), encoding='utf-8') as f:
            data[kind] = json.load(f)
    return data


def check_icons(data):
    print('== 1. 图标覆盖 ==')
    missing = {}   # 材料名 -> [配方出处...]
    total = 0
    for kind, recs_map in data.items():
        for name, recs in recs_map.items():
            for r in recs:
                total += 1
                cells = []
                if r.get('grid'):
                    cells.extend(m for m in r['grid'].values() if m)
                for k in ('input', 'output', 'template', 'base', 'addition', 'ingredient'):
                    v = r.get(k)
                    if v:
                        cells.extend(v if isinstance(v, list) else [v])
                for m in cells:
                    for part in str(m).split(';'):
                        part = part.strip()
                        if not part:
                            continue
                        if load_icon(part) is None and part.split(',')[0].strip():
                            missing.setdefault(part, []).append(f'{name}({kind})')
    if not missing:
        print(f'  通过：{total} 条配方全部图标可解析')
        return True
    print(f'  缺失 {len(missing)} 种图标（共 {total} 条配方）：')
    for m, src in sorted(missing.items()):
        print(f'    ✗ {m}  <- {src[0]}' + (f' 等{len(src)}处' if len(src) > 1 else ''))
    return False


def check_desc(data):
    print('== 2. 描述覆盖 ==')
    _load()
    miss = []
    for kind, recs_map in data.items():
        for name in recs_map:
            if name in DESC_ALLOW_MISS:
                continue
            if query_desc(name) is None:
                miss.append(f'{name}({kind})')
    if not miss:
        print('  通过：全部配方条目都能查到描述')
        return True
    print(f'  缺失描述 {len(miss)} 条：')
    for m in miss:
        print(f'    ✗ {m}')
    return False


def check_variants():
    print('== 3. 变体完整性（16 色家族） ==')
    _load()
    from astrbot_plugin_mcquery_v3.desc_query import _items, _vm
    covered = set(_items) | set(_vm)
    bad = []
    for suf in MUST_16_FAMILIES:
        absent = [c for c in MUST_16_COLORS if (c + suf) not in covered]
        if absent:
            bad.append(f'{suf} 缺 {"/".join(absent)}')
    if not bad:
        print('  通过：所有 16 色家族颜色齐全')
        return True
    print(f'  缺失 {len(bad)} 处：')
    for b in bad:
        print(f'    ✗ {b}')
    return False


def check_shapeless(data):
    print('== 4. 无序标记 ==')
    bad = []
    for name in KNOWN_SHAPELESS:
        recs = data['craft'].get(name, [])
        if not recs:
            bad.append(f'{name} 无配方数据')
            continue
        for i, r in enumerate(recs):
            if not r.get('shapeless'):
                bad.append(f'{name}[{i}] 缺 shapeless 标记')
    if not bad:
        print('  通过：已知无序配方均已标记 shapeless')
        return True
    for b in bad:
        print(f'    ✗ {b}')
    return False


def main():
    print('mcquery_v3 数据自检\n' + '-' * 40)
    data = load_prescriptions()
    ok = True
    ok &= check_icons(data)
    ok &= check_desc(data)
    ok &= check_variants()
    ok &= check_shapeless(data)
    print('-' * 40)
    print('结论：' + ('全部通过 ✅' if ok else '存在缺口，请按上文修复 ❌'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

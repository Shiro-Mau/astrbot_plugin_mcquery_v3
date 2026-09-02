# -*- coding: utf-8 -*-
"""查询引擎：物品(配方+描述)、成就、目录。不依赖 astrbot，可独立测试。"""
import os, json, math
from pathlib import Path

BASE = Path(__file__).resolve().parent

from .render_mq import render_full
from .desc_query import query_desc, normalize_candidates
from .desc_render import render_desc
from .advancements import query_adv
from .render_adv import render_adv
from . import catalog_build as cb
from . import render_catalog as rc

OUT = os.path.join(str(BASE), 'out')


def _save(img, sub):
    d = os.path.join(OUT, 'query')
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, sub + '.png')
    img.save(p)
    return p


# ---------------- 配方数据 ----------------
_PRESC = None


def _prescription():
    global _PRESC
    if _PRESC is None:
        _PRESC = {}
        P = os.path.join(str(BASE), 'mcquery_v3', 'Prescription')
        for kind, fn in [('craft', 'crafting.json'), ('smelt', 'smelting.json'),
                         ('smith', 'smithing.json'), ('stonecut', 'stonecutting.json'),
                         ('brew', 'brewing.json')]:
            with open(os.path.join(P, fn), encoding='utf-8') as f:
                data = json.load(f)
            for name, recs in data.items():
                _PRESC.setdefault(name, []).extend((kind, r) for r in recs)
    return _PRESC


# ---------------- 物品查询 ----------------
def query_item(name):
    """返回 (图片路径列表, 提示文本)。顺序：先描述后配方。"""
    imgs = []
    # 彩蛋：莎莎
    if name.strip() == '莎莎':
        img = render_desc('莎莎', '', 'shasha', [('', '是一个笨蛋傲娇')], tips='')
        imgs.append(_save(img, '莎莎_描述'))
        return imgs, ''
    d = query_desc(name)
    if d:
        img = render_desc(d['title'], d['en'], d['icon'], d['sections'], lead=d['lead'])
        imgs.append(_save(img, f'{name}_描述'))
    presc = _prescription()
    for c in normalize_candidates(name):
        recs = presc.get(c)
        if recs:
            for i, (kind, rec) in enumerate(recs):
                img = render_full(kind, rec)
                imgs.append(_save(img, f'{name}_配方{i}'))
            break
    if not imgs:
        return [], '未查询到该物品，请确认名称是否正确'
    return imgs, ''


# ---------------- 成就查询 ----------------
def query_achievement(name):
    """返回 (图片路径列表, 提示文本)。"""
    r = query_adv(name)
    if not r:
        return [], '未查询到该进度，请确认名称是否正确'
    if 'ambiguous' in r:
        return [], '多个匹配，请输入完整名称：' + '、'.join(r['ambiguous'])
    img = render_adv(r, r.get('upstream_name', ''))
    return [_save(img, f'成就_{name}')], ''


# ---------------- 目录 ----------------
_CAT = {}


def catalog(kind):
    """kind: 'item'/'block'/'adv'。返回 [(路径, 首字母或None), ...]"""
    if kind in _CAT:
        return _CAT[kind]
    out_dir = os.path.join(OUT, f'cat_{kind}')
    os.makedirs(out_dir, exist_ok=True)
    if kind == 'adv':
        entries = sorted(cb.load_adv(), key=lambda e: rc.pinyin_key(e[0]))
        title, ck = '成就', 'adv'
    else:
        items, blocks = cb.parse_list()
        entries = cb.sort_entries(items if kind == 'item' else blocks)
        title, ck = ('物品', 'item') if kind == 'item' else ('方块', 'block')
    cap = 4 * 32
    pages = []
    if len(entries) <= cap:
        img = rc.render_page(title, f'共 {len(entries)} 项', entries, ck, 1, 1)
        p = os.path.join(out_dir, 'p01.png')
        img.save(p)
        pages.append((p, None))
    else:
        groups = cb.group_by_letter(entries)
        total = sum(math.ceil(len(g) / cap) for g in groups.values())
        i = 0
        for letter, g in groups.items():
            while g:
                chunk, g = g[:cap], g[cap:]
                i += 1
                sub = f'首字母 {letter.upper()} · 共 {len(chunk)} 项'
                img = rc.render_page(title, sub, chunk, ck, i, total)
                p = os.path.join(out_dir, f'p{i:02d}.png')
                img.save(p)
                pages.append((p, letter))
    _CAT[kind] = pages
    return pages


def catalog_all(kind):
    """返回目录全部页的路径列表（不翻页，一次性发完）。"""
    return [p for p, _ in catalog(kind)]


def catalog_page(kind, arg):
    """根据页码(数字)或首字母定位目录页。返回 (路径, 提示, 总页数)。"""
    pages = catalog(kind)
    total = len(pages)
    if arg is None:
        p, letter = pages[0]
        tail = f'共 {total} 页' if total > 1 else ''
        return p, tail, total
    if arg.isdigit():
        idx = int(arg) - 1
        if idx < 0 or idx >= total:
            return None, f'页码超出范围，共 {total} 页', total
        p, _ = pages[idx]
        return p, f'{idx + 1}/{total} 页', total
    letter = arg.lower()
    for p, L in pages:
        if L == letter:
            return p, f'首字母 {letter.upper()}', total
    return None, f'没有以 {letter.upper()} 开头的条目', total

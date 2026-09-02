# -*- coding: utf-8 -*-
"""目录数据准备 + 分页渲染（成就/物品/方块）"""
import os, re, json, math
from collections import OrderedDict
from render_catalog import render_page, pinyin_key, _first_letter

BASE = os.path.dirname(os.path.abspath(__file__))

# ---- 补充映射：items.json / variant_map 查不到的中文名 -> 英文图标名 ----
TECH_MAP = {
    # 唱片
    '音乐唱片（5）': 'Music Disc 5', '音乐唱片（11）': 'Music Disc 11',
    '音乐唱片（13）': 'Music Disc 13', '音乐唱片（blocks）': 'Music Disc Blocks',
    '音乐唱片（Bounce）': 'Music Disc Bounce', '音乐唱片（cat）': 'Music Disc Cat',
    '音乐唱片（chirp）': 'Music Disc Chirp', '音乐唱片（Creator）': 'Music Disc Creator',
    '音乐唱片（Creator（八音盒））': 'Music Disc Creator (Music Box)',
    '音乐唱片（far）': 'Music Disc Far', '音乐唱片（Lava Chicken）': 'Music Disc Lava Chicken',
    '音乐唱片（mall）': 'Music Disc Mall', '音乐唱片（mellohi）': 'Music Disc Mellohi',
    '音乐唱片（otherside）': 'Music Disc Otherside', '音乐唱片（Pigstep）': 'Music Disc Pigstep',
    '音乐唱片（Precipice）': 'Music Disc Precipice', '音乐唱片（Relic）': 'Music Disc Relic',
    '音乐唱片（stal）': 'Music Disc Stal', '音乐唱片（strad）': 'Music Disc Strad',
    '音乐唱片（Tears）': 'Music Disc Tears', '音乐唱片（wait）': 'Music Disc Wait',
    '音乐唱片（ward）': 'Music Disc Ward',
    # 锻造模板
    '锻造模板（下界合金升级）': 'Netherite Upgrade',
    '锻造模板（镶铆盔甲纹饰）': 'Bolt Armor Trim', '锻造模板（海岸盔甲纹饰）': 'Coast Armor Trim',
    '锻造模板（沙丘盔甲纹饰）': 'Dune Armor Trim', '锻造模板（眼眸盔甲纹饰）': 'Eye Armor Trim',
    '锻造模板（涡流盔甲纹饰）': 'Flow Armor Trim', '锻造模板（雇主盔甲纹饰）': 'Host Armor Trim',
    '锻造模板（牧民盔甲纹饰）': 'Raiser Armor Trim', '锻造模板（肋骨盔甲纹饰）': 'Rib Armor Trim',
    '锻造模板（哨兵盔甲纹饰）': 'Sentry Armor Trim', '锻造模板（塑造盔甲纹饰）': 'Shaper Armor Trim',
    '锻造模板（幽静盔甲纹饰）': 'Silence Armor Trim', '锻造模板（猪鼻盔甲纹饰）': 'Snout Armor Trim',
    '锻造模板（尖塔盔甲纹饰）': 'Spire Armor Trim', '锻造模板（潮汐盔甲纹饰）': 'Tide Armor Trim',
    '锻造模板（恼鬼盔甲纹饰）': 'Vex Armor Trim', '锻造模板（监守盔甲纹饰）': 'Ward Armor Trim',
    '锻造模板（向导盔甲纹饰）': 'Wayfinder Armor Trim', '锻造模板（荒野盔甲纹饰）': 'Wild Armor Trim',
    # 技术方块 / 特殊
    '地图及探险家地图': 'Empty Map',
    '屏障': 'Barrier', '命令方块': 'Command Block', '连锁型命令方块': 'Chain Command Block',
    '循环型命令方块': 'Repeating Command Block', '结构方块': 'Structure Block', '结构空位': 'Structure Void',
    '拼图方块': 'Jigsaw Block', '光源方块': 'Light 0', '刷怪笼': 'Monster Spawner',
    '试炼刷怪笼': 'Trial Spawner', '末地传送门框架': 'End Portal Frame',
    '熔岩': 'Lava', '细雪': 'Powder Snow', '灵魂火': 'Soul Fire', '气泡柱': 'Bubble Column',
    '切石机（MATTIS）': 'Stonecutter',
    '白色羊毛楼梯': 'White Wool Stairs',
    # 虫蚀方块复用普通方块图标
    '虫蚀石头': 'Stone', '虫蚀圆石': 'Cobblestone', '虫蚀石砖': 'Stone Bricks',
    '虫蚀苔石砖': 'Mossy Stone Bricks', '虫蚀裂纹石砖': 'Cracked Stone Bricks',
    '虫蚀雕纹石砖': 'Chiseled Stone Bricks', '虫蚀深板岩': 'Deepslate',
}

_items = None
_variant = None
_vicon = None


def _load():
    global _items, _variant, _vicon
    if _items is None:
        _items = json.load(open(os.path.join(BASE, 'mcquery_v3', 'Database', 'items.json'), encoding='utf-8'))
        _variant = json.load(open(os.path.join(BASE, 'mcquery_v3', 'Database', 'variant_map.json'), encoding='utf-8'))
        _vicon = json.load(open(os.path.join(BASE, 'mcquery_v3', 'Database', 'variant_icon_map.json'), encoding='utf-8'))


def resolve_icon(cn):
    _load()
    if cn in _items:
        return _items[cn].get('icon', '')
    p = _variant.get(cn)
    if p and p in _items:
        return _vicon.get(cn) or _items[p].get('icon', '')
    return TECH_MAP.get(cn, '')


def clean_name(s):
    s = re.sub(r'\[[^\]]*\]', '', s)
    s = re.sub(r'（(?:作为|仅)[^）]*）', '', s)
    s = s.rstrip(']').strip()
    m = re.search(r'精灵图 (.+)$', s)          # BlockSprite 残留 -> 末尾中文名
    if m:
        s = m.group(1)
    return s


def _is_note(s):
    return len(s) > 20 and ('，' in s or '。' in s)


TITLES = ['产生方块、液体或实体的物品', '在世界中可以交互的物品', '在世界中间接使用的物品', '方块列表', '技术性方块']


def parse_list():
    lines = [ln.strip() for ln in open(os.path.join(BASE, 'items_list.txt'), encoding='utf-8').read().split('\n') if ln.strip()]
    sec = {}; cur = None
    for ln in lines:
        if ln in TITLES:
            cur = ln; sec[cur] = []
        elif cur:
            sec[cur].append(ln)
    items = []
    for t in TITLES[:3]:
        for raw in sec.get(t, []):
            cn = clean_name(raw)
            if cn and not _is_note(cn):
                items.append(cn)
    blocks = []
    for raw in sec.get('方块列表', []):
        cn = clean_name(raw)
        if cn and not _is_note(cn):
            blocks.append(cn)
    for raw in sec.get('技术性方块', []):
        cn = clean_name(raw)
        if cn and not _is_note(cn):
            blocks.append(cn)
    return items, blocks


def load_adv():
    advs = json.load(open(os.path.join(BASE, 'mcquery_v3', 'Accom_Database', 'advancements.json'), encoding='utf-8'))
    return [(a['title_zh'], a.get('icon', ''), a.get('bg', 'plain')) for a in advs]


def sort_entries(names):
    """返回 [(中文名, icon, bg)]，按拼音排序，重复名去重"""
    seen = set()
    out = []
    for cn in sorted(names, key=pinyin_key):
        if cn in seen:
            continue
        seen.add(cn)
        out.append((cn, resolve_icon(cn), None))
    return out


def group_by_letter(entries):
    groups = OrderedDict()
    for e in entries:
        k = _first_letter(e[0])
        groups.setdefault(k, []).append(e)
    return groups


def render_all(kind, title, entries, out_dir, max_rows=32):
    """按首字母分页渲染；整组一页能容下则合并（不分字母）"""
    os.makedirs(out_dir, exist_ok=True)
    cap = 4 * max_rows
    pages = []
    if len(entries) <= cap:
        pages.append((title, f'共 {len(entries)} 项', entries))
    else:
        for k, g in group_by_letter(entries).items():
            while g:
                chunk, g = g[:cap], g[cap:]
                sub = f'首字母 {k.upper()} · 共 {len(chunk)} 项'
                pages.append((title, sub, chunk))
    total = len(pages)
    saved = []
    for i, (t, sub, es) in enumerate(pages, 1):
        img = render_page(t, sub, es, kind, i, total)
        p = os.path.join(out_dir, f'{title}_{i:02d}.png')
        img.save(p)
        saved.append(p)
    return saved, total


if __name__ == '__main__':
    # 成就：一页
    adv = load_adv()
    adv = sorted(adv, key=lambda e: pinyin_key(e[0]))
    print('成就:', len(adv))
    # 物品 / 方块
    items, blocks = parse_list()
    print('物品(原始):', len(items), ' 方块(含技术):', len(blocks))
    item_entries = sort_entries(items)
    block_entries = sort_entries(blocks)
    print('物品(去重):', len(item_entries), ' 方块(去重):', len(block_entries))
    no_icon = [e[0] for e in item_entries + block_entries if not e[1]]
    print('仍无图标:', len(no_icon))
    for n in no_icon:
        print('   ', n)
    # 字母分布
    for name, es in [('物品', item_entries), ('方块', block_entries)]:
        g = group_by_letter(es)
        print(f'\n{name} 字母分布:', {k: len(v) for k, v in g.items()})
    # 出成就样图
    pages, total = render_all('adv', '成就', adv, 'render_test/catalog_adv')
    print(f'\n成就目录: {total} 页 ->', pages)

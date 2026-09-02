# -*- coding: utf-8 -*-
"""mq 查询渲染：配方 + 图标 → 图"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

_BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _BASE)
from .potion_icon_map import potion_icon
from .subtitle import recipe_subtitle

BASE = os.path.join(_BASE, 'mcquery_v3')
T = os.path.join(BASE, 'Template')
M = os.path.join(BASE, 'Material')
P = os.path.join(BASE, 'Prescription')

# 各模板槽位坐标（图标粘贴左上角）
CG = {'A1': (46, 34), 'B1': (82, 34), 'C1': (118, 34),
      'A2': (46, 70), 'B2': (82, 70), 'C2': (118, 70),
      'A3': (46, 106), 'B3': (82, 106), 'C3': (118, 106)}
CO_CRAFT = (233, 69)

FURNACE_IN = (96, 46)
FURNACE_FUEL = (96, 118)
FURNACE_OUT = (216, 82)

SMITH = {'template': (16, 96), 'base': (52, 96), 'addition': (88, 96)}
SMITH_OUT = (196, 96)

# 酿造台 6 槽：燃料(左)、材料(中上)、成品(右上)、基底药水x3(底部)
BREW_FUEL = (34, 25)
BREW_MAT = (158, 25)
BREW_OUT = (244, 21)
BREW_BASE3 = [(112, 93), (158, 107), (204, 93)]

# 切石机：材料格(左)、切石机图标(中,固定)、输出格(右) —— 图标左上角
STONECUT_IN = (82, 64)
STONECUT_MID = (128, 39)
STONECUT_OUT = (200, 66)

# tag 材料 → 代表图标
TAG_REP = {'planks': 'Oak Planks', 'logs': 'Oak Log', 'acacia_logs': 'Acacia Log',
           'birch_logs': 'Birch Log', 'cherry_logs': 'Cherry Log', 'dark_oak_logs': 'Dark Oak Log',
           'jungle_logs': 'Jungle Log', 'mangrove_logs': 'Mangrove Log', 'oak_logs': 'Oak Log',
           'pale_oak_logs': 'Pale Oak Log', 'spruce_logs': 'Spruce Log', 'crimson_stems': 'Crimson Stem',
           'warped_stems': 'Warped Stem', 'wooden_slabs': 'Oak Slab', 'wool': 'White Wool',
           'banners': 'White Banner', 'bundles': 'Bundle', 'shulker_boxes': 'Shulker Box',
           'eggs': 'Egg', 'coals': 'Coal', 'leaves': 'Oak Leaves', 'skulls': 'Skeleton Skull',
           'logs_that_burn': 'Oak Log', 'stone_crafting_materials': 'Cobblestone',
           'bamboo_blocks': 'Block of Bamboo', 'book_cloning_target': 'Written Book',
           'decorated_pot_ingredients': 'Brick', 'smelts_to_glass': 'Sand',
           'soul_fire_base_blocks': 'Soul Sand', 'metal_nuggets': 'Iron Nugget', 'dyes': 'White Dye',
           'stone': 'Cobblestone', 'bed': 'White Bed', 'carpet': 'White Carpet', 'harness': 'White Harness'}
for t, v in {'iron': 'Iron Ingot', 'gold': 'Gold Ingot', 'diamond': 'Diamond',
             'netherite': 'Netherite Ingot', 'stone': 'Cobblestone', 'copper': 'Copper Ingot',
             'wooden': 'Oak Planks'}.items():
    TAG_REP[f'{t}_tool_materials'] = v
TAG_REP['cushion'] = 'White Cushion'
TAG_REP['wool_slab'] = 'White Wool Slab'
TAG_REP['wool_stairs'] = 'White Wool Stairs'


def load_icon(name):
    """配方里的名字 → 图标 Image（或 None）"""
    if not name:
        return None
    n = name.strip()
    if n.startswith('Any '):
        n = TAG_REP.get(n[4:].replace(' ', '_').lower(), n[4:])
    n = n.split(';')[0].strip().split(',')[0].strip()
    if n.startswith('Waxed '):
        n = n[6:]  # 涂蜡变体与基础物品外观一致，复用基础图标
    n = potion_icon(n)
    if not n:
        return None
    p = os.path.join(M, n + '.png')
    if os.path.exists(p):
        return Image.open(p).convert('RGBA')
    pg = os.path.join(M, n + '.gif')
    if os.path.exists(pg):
        return Image.open(pg).convert('RGBA')
    return None


def render_craft(recipe):
    bg = Image.open(os.path.join(T, 'crafting_table.png')).convert('RGBA')
    # 纯数据驱动：grid 摆哪格就画哪格（有序/无序无所谓，信息由字幕承载）
    for cell, mat in recipe.get('grid', {}).items():
        p = CG.get(cell)
        if p and mat:
            ic = load_icon(mat)
            if ic:
                bg.paste(ic, p, ic)
    out = load_icon(recipe.get('output', ''))
    if out:
        bg.paste(out, CO_CRAFT, out)
    return bg


def render_smelt(recipe):
    bg = Image.open(os.path.join(T, 'furnace.png')).convert('RGBA')
    inp = recipe.get('input', [])
    ic = load_icon(inp[0] if inp else '')
    if ic:
        bg.paste(ic, FURNACE_IN, ic)
    # 燃料槽固定放煤炭
    fuel = load_icon('Coal')
    if fuel:
        bg.paste(fuel, FURNACE_FUEL, fuel)
    out = load_icon(recipe.get('output', ''))
    if out:
        bg.paste(out, FURNACE_OUT, out)
    return bg


def render_smith(recipe):
    bg = Image.open(os.path.join(T, 'smithing_table.png')).convert('RGBA')
    for k, pos in SMITH.items():
        ic = load_icon(recipe.get(k, ''))
        if ic:
            bg.paste(ic, pos, ic)
    out = load_icon(recipe.get('output', ''))
    if out:
        bg.paste(out, SMITH_OUT, out)
    return bg


def render_brew(recipe):
    bg = Image.open(os.path.join(T, 'brewing_stand.png')).convert('RGBA')
    # 燃料槽固定烈焰粉
    fuel = load_icon('Blaze Powder')
    if fuel:
        bg.paste(fuel, BREW_FUEL, fuel)
    # 材料（中间上）
    ic = load_icon(recipe.get('ingredient', ''))
    if ic:
        bg.paste(ic, BREW_MAT, ic)
    # 成品（右上）
    out = load_icon(recipe.get('output', ''))
    if out:
        bg.paste(out, BREW_OUT, out)
    # 基底药水 x3（底部）
    base = load_icon(recipe.get('base', ''))
    if base:
        for pos in BREW_BASE3:
            bg.paste(base, pos, base)
    return bg


def render_stonecut(recipe):
    bg = Image.open(os.path.join(T, 'stonecutter.png')).convert('RGBA')
    # 材料格（左）
    inp = recipe.get('input', [])
    ic = load_icon(inp[0] if inp else '')
    if ic:
        bg.paste(ic, STONECUT_IN, ic)
    # 切石机图标（中，固定，Java 版 gif）
    cutter_p = os.path.join(M, 'Stonecutter.gif')
    if os.path.exists(cutter_p):
        cutter = Image.open(cutter_p).convert('RGBA')
        bg.paste(cutter, STONECUT_MID, cutter)
    # 输出格（右）
    out = load_icon(recipe.get('output', ''))
    if out:
        bg.paste(out, STONECUT_OUT, out)
    return bg



def _find_font():
    """按平台查找可用中文字体(Windows 优先, 兼容 Linux/macOS)"""
    import os
    cands = [
        r'C:\Windows\Fonts\msyh.ttc', r'C:\Windows\Fonts\msyh.ttf',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/System/Library/Fonts/PingFang.ttc',
    ]
    for p in cands:
        if os.path.exists(p):
            return p
    return cands[0]

FONT_PATH = _find_font()


def add_subtitle(img, text, padding_x=12):
    """在图片下方加白底黑字字幕栏，超宽自动换行"""
    if not text:
        return img
    W = img.width
    size = 22
    font = ImageFont.truetype(FONT_PATH, size)
    max_w = W - padding_x * 2
    # 逐字符换行
    lines = []
    line = ''
    for ch in text:
        if line and ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(line + ch, font=font) > max_w:
            lines.append(line)
            line = ch
        else:
            line += ch
    if line:
        lines.append(line)
    line_h = size + 6
    pad_top = 8
    bar_h = pad_top * 2 + line_h * len(lines)
    new = Image.new('RGB', (W, img.height + bar_h), 'white')
    new.paste(img, (0, 0))
    draw = ImageDraw.Draw(new)
    y = img.height + pad_top
    for ln in lines:
        tw = draw.textlength(ln, font=font)
        draw.text(((W - tw) / 2, y), ln, fill='black', font=font)
        y += line_h
    return new


def render_full(kind, recipe):
    """渲染配方图 + 字幕，返回最终图片"""
    if kind == 'craft':
        img = render_craft(recipe)
    elif kind == 'smelt':
        img = render_smelt(recipe)
    elif kind == 'smith':
        img = render_smith(recipe)
    elif kind == 'stonecut':
        img = render_stonecut(recipe)
    else:
        img = render_brew(recipe)
    text = recipe_subtitle({'craft': 'crafting', 'smelt': 'smelting',
                            'smith': 'smithing', 'stonecut': 'stonecutting',
                            'brew': 'brewing'}.get(kind, kind), recipe)
    return add_subtitle(img, text)


def main():
    out_dir = 'render_test'
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(P, 'crafting.json'), encoding='utf-8') as f:
        crafting = json.load(f)
    with open(os.path.join(P, 'smelting.json'), encoding='utf-8') as f:
        smelting = json.load(f)
    with open(os.path.join(P, 'smithing.json'), encoding='utf-8') as f:
        smithing = json.load(f)
    with open(os.path.join(P, 'brewing.json'), encoding='utf-8') as f:
        brewing = json.load(f)

    jobs = [
        ('craft', crafting['工作台'][0], '工作台'),
        ('craft', crafting['弩'][0], '弩'),
        ('craft', crafting['铁锭'][0], '铁锭_铁块分解'),
        ('craft', crafting['铁锭'][1], '铁锭_铁粒合成'),
        ('smelt', smelting['铁锭'][1], '铁锭_熔炼'),
        ('smelt', smelting['金锭'][1], '金锭'),
        ('smelt', smelting['玻璃'][0], '玻璃'),
        ('smelt', smelting['钻石'][1], '钻石'),
        ('smith', smithing['下界合金剑'][0], '下界合金剑'),
        ('smith', smithing['下界合金胸甲'][0], '下界合金胸甲'),
        ('brew', brewing['力量药水'][0], '力量药水'),
        ('brew', brewing['治疗药水'][0], '治疗药水'),
        ('brew', brewing['夜视药水'][0], '夜视药水'),
    ]
    for typ, recipe, name in jobs:
        img = render_full(typ, recipe)
        p = os.path.join(out_dir, f'mq_{typ}_{name}.png')
        img.save(p)
        print(f'  ✓ {p} ({img.size[0]}x{img.size[1]})')


if __name__ == '__main__':
    main()

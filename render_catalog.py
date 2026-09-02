# -*- coding: utf-8 -*-
"""目录页渲染：条目(左图标+右名字)按多列网格排列，套成就模板草方块+泥土配色"""
import os, math
from PIL import Image, ImageDraw, ImageFont
from pypinyin import lazy_pinyin


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

FONT = _find_font()
_BASE = os.path.dirname(os.path.abspath(__file__))
MAT = os.path.join(_BASE, 'mcquery_v3', 'Material')
ACCOM_MAT = os.path.join(_BASE, 'mcquery_v3', 'Accom_Material')

GRASS = (107, 154, 61)
DIRT = (155, 118, 83)
DIRT_DARK = (120, 88, 60)
BORDER = (78, 52, 46)
TEXT_TITLE = (255, 255, 255)
TEXT_SUB = (230, 240, 210)
TEXT_BODY = (248, 236, 210)

COLUMNS = 4
COL_W = 180
GAP = 8
PAD = 20
ROW_H = 44
ICON_S = 32
NAME_FONT_S = 18


def load_mat_icon(name):
    if not name:
        return None
    base = name
    for ext in ('.gif', '.png'):
        if base.lower().endswith(ext):
            base = base[:-len(ext)]
            break
    for ext in ('.png', '.gif'):
        p = os.path.join(MAT, base + ext)
        if os.path.exists(p):
            return Image.open(p).convert('RGBA')
    return None


def build_entry_icon(icon_name, bg, kind):
    """kind: 'adv' 用进度背景框+图标；否则用 Invicon"""
    if kind == 'adv':
        try:
            import render_adv
            img = render_adv.build_icon(icon_name, bg or 'plain')
        except Exception:
            img = None
        if img:
            return img.resize((ICON_S, ICON_S), Image.LANCZOS)
        return None
    img = load_mat_icon(icon_name)
    if img:
        return img.resize((ICON_S, ICON_S), Image.LANCZOS)
    return None


def pinyin_key(name):
    return ''.join(lazy_pinyin(name)).lower()


def _first_letter(name):
    py = ''.join(lazy_pinyin(name)).lower()
    return py[0] if py else '#'


def _fit_name_font(draw, text, maxw):
    size = NAME_FONT_S
    while size > 11:
        f = ImageFont.truetype(FONT, size)
        if draw.textlength(text, font=f) <= maxw:
            return f
        size -= 1
    return ImageFont.truetype(FONT, 11)


def _wrap_text(draw, text, font, maxw):
    lines = []
    line = ''
    for ch in text:
        if line and draw.textlength(line + ch, font=font) > maxw:
            lines.append(line)
            line = ch
        else:
            line += ch
    if line:
        lines.append(line)
    return lines


def render_page(title, subtitle, entries, kind, page_no=1, total_pages=1):
    """渲染一页目录。
    entries: [(中文名, 图标名, bg)]
    4 列网格，第一行标题 + 副标题（字母/页码）。
    """
    n = len(entries)
    per_col = max(1, math.ceil(n / COLUMNS))
    head_h = 92
    W = PAD * 2 + COL_W * COLUMNS + GAP * (COLUMNS - 1)
    H = head_h + 14 + per_col * ROW_H + PAD

    canvas = Image.new('RGBA', (W, H), DIRT)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, W, head_h], fill=GRASS)
    for i in range(8):
        draw.line([0, head_h - 8 + i, W, head_h - 8 + i],
                  fill=(GRASS[0] - i * 3, GRASS[1] - i * 3, GRASS[2] - i * 2))
    draw.rectangle([0, 0, W - 1, H - 1], outline=BORDER, width=6)

    f_title = ImageFont.truetype(FONT, 34)
    f_sub = ImageFont.truetype(FONT, 20)
    f_name = ImageFont.truetype(FONT, NAME_FONT_S)

    draw.text((PAD, 14), title, fill=TEXT_TITLE, font=f_title)
    sub = f'{subtitle}　{page_no}/{total_pages}' if total_pages > 1 else subtitle
    tw = draw.textlength(sub, font=f_sub)
    draw.text((W - PAD - tw, head_h - 38), sub, fill=TEXT_SUB, font=f_sub)

    line_y = head_h + 6
    draw.line([PAD, line_y, W - PAD, line_y], fill=DIRT_DARK, width=2)

    y0 = line_y + 10
    name_maxw = COL_W - ICON_S - 8 - 4
    for idx, (cn, icon_name, bg) in enumerate(entries):
        col = idx // per_col
        row = idx % per_col
        x = PAD + col * (COL_W + GAP)
        y = y0 + row * ROW_H
        icon = build_entry_icon(icon_name, bg, kind)
        if icon is not None:
            canvas.paste(icon, (x, y + (ROW_H - ICON_S) // 2), icon)
        else:
            draw.rectangle([x, y + 6, x + ICON_S, y + 6 + ICON_S],
                           fill=(90, 90, 90, 255), outline=(60, 60, 60, 255))
        f = _fit_name_font(draw, cn, name_maxw)
        if draw.textlength(cn, font=f) <= name_maxw:
            draw.text((x + ICON_S + 8, y + (ROW_H - f.size) // 2 - 2), cn,
                      fill=TEXT_BODY, font=f)
        else:
            for li, ln in enumerate(_wrap_text(draw, cn, f, name_maxw)[:2]):
                draw.text((x + ICON_S + 8, y + 5 + li * (f.size + 2)), ln,
                          fill=TEXT_BODY, font=f)
    return canvas.convert('RGB')

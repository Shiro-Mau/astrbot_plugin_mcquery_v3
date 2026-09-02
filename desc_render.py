# -*- coding: utf-8 -*-
"""Minecraft 物品/成就介绍图渲染（草方块+泥土配色）"""
import os
from PIL import Image, ImageDraw, ImageFont

def _find_font():
    """按平台查找可用的中文像素字体(Windows 优先, 兼容 Linux/macOS)"""
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

# 草方块 + 泥土配色
GRASS = (107, 154, 61)
DIRT = (155, 118, 83)
DIRT_DARK = (120, 88, 60)
BORDER = (78, 52, 46)
TEXT_TITLE = (255, 255, 255)
TEXT_SUB = (230, 240, 210)
TEXT_HEAD = (255, 224, 130)
TEXT_BODY = (248, 236, 210)


def _wrap(draw, text, font, maxw):
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


def _fit_font(draw, text, max_size, maxw):
    """标题超宽时逐级缩小字号，保证不越界"""
    size = max_size
    while size > 16:
        f = ImageFont.truetype(FONT, size)
        if draw.textlength(text, font=f) <= maxw:
            return f
        size -= 2
    return ImageFont.truetype(FONT, 16)


def render_desc(title, en, icon_name, sections, lead='', tips='Tips: 数据来源于 Minecraft 中文Wiki', frame=True):
    """渲染介绍图。sections = [(小标题, 内容), ...]（小标题为空串则只写正文）"""
    W = 800
    PAD = 36
    f_title = ImageFont.truetype(FONT, 38)
    f_sub = ImageFont.truetype(FONT, 18)
    f_tips = ImageFont.truetype(FONT, 17)
    f_head = ImageFont.truetype(FONT, 24)
    f_body = ImageFont.truetype(FONT, 21)

    tmp = ImageDraw.Draw(Image.new('RGBA', (W, 1)))
    head_h = 96
    y = head_h + 28
    if lead:
        y += len(_wrap(tmp, lead, f_body, W - PAD * 2)) * 28 + 8
    for head, body in sections:
        if head:
            y += 30
        y += len(_wrap(tmp, body, f_body, W - PAD * 2)) * 28
        y += 8
    H = y + PAD

    canvas = Image.new('RGBA', (W, H), DIRT)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, W, head_h], fill=GRASS)
    for i in range(8):
        draw.line([0, head_h - 8 + i, W, head_h - 8 + i],
                  fill=(GRASS[0] - i * 3, GRASS[1] - i * 3, GRASS[2] - i * 2))
    draw.rectangle([0, 0, W - 1, H - 1], outline=BORDER, width=6)

    # 图标 + 名字 + Tips
    icon_path = os.path.join(MAT, icon_name + '.png')
    if not os.path.exists(icon_path):
        icon_path = os.path.join(MAT, icon_name + '.gif')
    if os.path.exists(icon_path):
        icon = Image.open(icon_path).convert('RGBA').resize((64, 64), Image.LANCZOS)
        slot_x, slot_y = PAD, 16
        if frame:
            draw.rectangle([slot_x - 5, slot_y - 5, slot_x + 69, slot_y + 69], fill=(198, 198, 198, 255))
            draw.rectangle([slot_x - 5, slot_y - 5, slot_x + 69, slot_y + 69], outline=(0, 0, 0, 255), width=3)
        canvas.paste(icon, (slot_x, slot_y), icon)
        name_x = slot_x + 64 + 26
    else:
        name_x = PAD
        slot_y = 16

    tw = draw.textlength(tips, font=f_tips)
    title_maxw = W - PAD - name_x - (tw + 24 if tw else 0)
    f_title_used = _fit_font(draw, title, 38, title_maxw)
    draw.text((name_x, slot_y + 4), title, fill=TEXT_TITLE, font=f_title_used)
    draw.text((name_x, slot_y + 48), en, fill=TEXT_SUB, font=f_sub)
    draw.text((W - PAD - tw, slot_y + 40), tips, fill=(240, 245, 220), font=f_tips)
    line_y = head_h + 20
    draw.line([PAD, line_y, W - PAD, line_y], fill=DIRT_DARK, width=2)

    y = line_y + 22
    if lead:
        for ln in _wrap(draw, lead, f_body, W - PAD * 2):
            draw.text((PAD, y), ln, fill=TEXT_BODY, font=f_body)
            y += 28
        y += 8
    for head, body in sections:
        if head:
            draw.text((PAD, y), head, fill=TEXT_HEAD, font=f_head)
            y += 30
        for ln in _wrap(draw, body, f_body, W - PAD * 2):
            draw.text((PAD, y), ln, fill=TEXT_BODY, font=f_body)
            y += 28
        y += 8

    return canvas.convert('RGB')


if __name__ == '__main__':
    img = render_desc('蜂巢', 'Bee Nest', 'Bee Nest', [
        ('', '蜂巢是作为蜜蜂巢穴的方块。'),
        ('自然生成', '每个蜂巢容纳 2-3 只蜜蜂，总是面朝南方。生成于樱花树林、繁花森林、草甸、原始桦木森林（树上 5% 概率）。'),
        ('树苗生成', '白桦/樱花树苗周围 2 格内有花时，长成的树有 5% 概率携带蜂巢。'),
        ('获取', '用精准采集破坏蜂巢获得。'),
    ])
    img.save(r'render_test\mq_desc_蜂巢_v3.png')
    print('OK', img.size)

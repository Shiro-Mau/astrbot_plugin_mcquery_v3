# -*- coding: utf-8 -*-
"""配方字幕：英文材料名 -> 中文名"""
import re

# ===== 基础映射：预生成的 en2cn.json（SPECIAL + EXTRA + 切石机产物） =====
def _load():
    import os, json
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, 'en2cn.json'), encoding='utf-8') as f:
        return json.load(f)

EN2CN = _load()

# ===== 材料（矿物）英文->中文 =====
MAT = {
    'Wooden':'木','Stone':'石','Iron':'铁','Gold':'金','Golden':'金',
    'Diamond':'钻石','Netherite':'下界合金','Copper':'铜','Chainmail':'锁链','Leather':'皮革',
    'Coal':'煤炭','Emerald':'绿宝石','Lapis Lazuli':'青金石','Quartz':'石英',
    'Redstone':'红石','Raw Copper':'粗铜','Raw Gold':'粗金','Raw Iron':'粗铁',
    'Resin':'树脂','Stripped Bamboo':'去皮竹',
}

# ===== 木材 =====
WOOD = {
    'Oak':'橡木','Birch':'白桦','Spruce':'云杉','Jungle':'丛林','Acacia':'金合欢',
    'Dark Oak':'深色橡木','Mangrove':'红树','Cherry':'樱花','Pale Oak':'苍白橡木',
    'Crimson':'绯红','Warped':'诡异','Bamboo':'竹',
}

# ===== 工具/护甲 =====
TOOL = {'Sword':'剑','Axe':'斧','Pickaxe':'镐','Shovel':'锹','Hoe':'锄','Spear':'矛','Fishing Rod':'钓竿'}
ARMOR = {'Helmet':'头盔','Chestplate':'胸甲','Leggings':'护腿','Boots':'靴子','Cap':'帽子','Tunic':'外套','Pants':'裤子','Horse Armor':'马铠'}

# ===== 颜色 =====
COLOR = {
    'White':'白色','Light Gray':'淡灰色','Gray':'灰色','Black':'黑色','Brown':'棕色',
    'Red':'红色','Orange':'橙色','Yellow':'黄色','Lime':'黄绿色','Green':'绿色',
    'Cyan':'青色','Light Blue':'淡蓝色','Blue':'蓝色','Purple':'紫色','Magenta':'品红色','Pink':'粉红色',
}
COLOR_SUFFIX = {
    'Dye':'染料','Wool':'羊毛','Bed':'床','Carpet':'地毯','Stained Glass':'染色玻璃',
    'Terracotta':'陶瓦','Banner':'旗帜','Harness':'挽具','Tulip':'郁金香',
    'Concrete':'混凝土','Concrete Powder':'混凝土粉末','Glazed Terracotta':'带釉陶瓦','Wool Stairs':'羊毛楼梯','Wool Slab':'羊毛台阶','Concrete Stairs':'混凝土楼梯','Concrete Slab':'混凝土台阶','Cushion':'坐垫',
}

# ===== 铜制品 & 氧化阶段 =====
COPPER_ITEM = {
    'Chiseled Copper':'雕纹铜块','Cut Copper':'切制铜块','Cut Copper Slab':'切制铜台阶','Cut Copper Stairs':'切制铜楼梯',
    'Copper Bulb':'铜灯','Copper Door':'铜门','Copper Trapdoor':'铜活板门','Copper Grate':'铜格栅',
    'Copper Bars':'铜栏杆','Copper Chain':'铜链','Copper Lantern':'铜灯笼','Copper Chest':'铜箱子',
    'Copper Golem Statue':'铜傀儡像','Lightning Rod':'避雷针',
}
COPPER_STAGE = {'Exposed':'斑驳','Weathered':'锈蚀','Oxidized':'氧化'}

# ===== 锻造模板 =====
ARMOR_TRIM = {
    'Coast':'海岸','Dune':'沙丘','Eye':'眼眸','Flow':'水流','Host':'雇主','Raiser':'牧者',
    'Rib':'肋骨','Sentry':'哨兵','Shaper':'塑造者','Silence':'静谧','Snout':'猪鼻','Spire':'尖塔',
    'Tide':'潮汐','Vex':'恼鬼','Ward':'监守者','Wayfinder':'指路者','Wild':'荒野',
}

# ===== 药水 =====
EFFECT = {
    'Fire Resistance':'抗火','Harming':'伤害','Healing':'治疗','Infestation':'虫蚀',
    'Invisibility':'隐身','Leaping':'跳跃','Night Vision':'夜视','Oozing':'软泥',
    'Poison':'中毒','Regeneration':'再生','Slow Falling':'缓降','Slowness':'缓慢',
    'Strength':'力量','Swiftness':'迅捷','Water Breathing':'水肺','Weakness':'虚弱',
    'Weaving':'织网','Wind Charging':'蓄风','the Turtle Master':'神龟之力',
}
POTION_SPECIAL = {
    'Awkward Potion':'粗制药水','Mundane Potion':'平凡的药水','Thick Potion':'浓稠的药水',
    'Awkward Splash Potion':'粗制的喷溅药水','Awkward Lingering Potion':'粗制的滞留药水',
    'Mundane Splash Potion':'平凡的喷溅药水','Mundane Lingering Potion':'平凡的滞留药水',
    'Thick Splash Potion':'浓稠的喷溅药水','Thick Lingering Potion':'浓稠的滞留药水',
    'Long Mundane Potion':'长效平凡的药水',
    'Splash Long Mundane Potion':'喷溅型长效平凡的药水',
    'Lingering Long Mundane Potion':'滞留型长效平凡的药水',
}

# ===== Any tag =====
TAG = {
    'Planks':'木板','Logs':'原木','Oak Logs':'橡木原木','Acacia Logs':'金合欢原木',
    'Birch Logs':'白桦原木','Cherry Logs':'樱花原木','Dark Oak Logs':'深色橡木原木',
    'Jungle Logs':'丛林原木','Mangrove Logs':'红树原木','Pale Oak Logs':'苍白橡木原木',
    'Spruce Logs':'云杉原木','Crimson Stems':'绯红菌柄','Warped Stems':'诡异菌柄',
    'Banners':'旗帜','Bundles':'收纳袋','Coals':'煤炭','Dyes':'染料','Eggs':'蛋',
    'Leaves':'树叶','Metal Nuggets':'金属粒','Shulker Boxes':'潜影盒','Skulls':'头颅',
    'Wool':'羊毛','Wool Stairs':'羊毛楼梯','Wool Slab':'羊毛台阶','Bed':'床','Carpet':'地毯','Cushion':'坐垫','Harness':'挽具','Stone':'石头类','Wooden Slabs':'木质台阶','Logs That Burn':'可燃原木',
    'Smelts To Glass':'可烧制成玻璃的物品','Soul Fire Base Blocks':'灵魂火基础方块',
    'Bamboo Blocks':'竹块','Book Cloning Target':'成书复制目标',
    'Decorated Pot Ingredients':'饰纹陶罐材料',
    'Copper Tool Materials':'铜质工具材料','Diamond Tool Materials':'钻石工具材料',
    'Gold Tool Materials':'金质工具材料','Iron Tool Materials':'铁质工具材料',
    'Netherite Tool Materials':'下界合金工具材料','Stone Tool Materials':'石质工具材料',
    'Wooden Tool Materials':'木质工具材料','Stone Crafting Materials':'石类合成材料',
}

# ===== 基础方块/花/杂项 =====
BLOCK = {
    'Allium':'绒球葱','Ancient Debris':'远古残骸','Andesite':'安山岩','Azure Bluet':'蓝花美耳草',
    'Basalt':'玄武岩','Blackstone':'黑石','Blue Orchid':'兰花','Brown Mushroom':'棕色蘑菇',
    'Cactus Flower':'仙人掌花','Clay':'黏土','Closed Eyeblossom':'闭合的眼眸花','Cobbled Deepslate':'深板岩圆石','Cobbled Deepslate Slab':'深板岩圆石台阶',
    'Cobblestone':'圆石','Cobweb':'蜘蛛网','Fishing Rod':'钓鱼竿','Cornflower':'矢车菊','Crying Obsidian':'哭泣的黑曜石',
    'Deepslate':'深板岩','Diorite':'闪长岩','Dirt':'泥土','End Stone':'末地石',
    'Glass':'玻璃','Glass Pane':'玻璃板','Glistering Melon Slice':'闪烁的西瓜片','Glowstone':'荧石',
    'Granite':'花岗岩','Gravel':'沙砾','Hay Bale':'干草捆','Straw Bed':'麦秆床','Ice':'冰',
    'Lily Of The Valley':'铃兰','Lilac':'丁香','Moss Block':'苔藓块','Mossy Cobblestone':'苔石',
    'Mud':'泥巴','Netherrack':'下界岩','Obsidian':'黑曜石','Open Eyeblossom':'开放的眼眸花',
    'Orange Tulip':'橙色郁金香','Oxeye Daisy':'滨菊','Packed Ice':'浮冰','Packed Mud':'泥坯',
    'Pale Moss Block':'苍白苔藓块','Peony':'牡丹','Pink Petals':'粉红色花簇','Pink Tulip':'粉红色郁金香',
    'Pitcher Plant':'瓶子草','Pointed Dripstone':'滴水石锥','Poppy':'虞美人','Red Mushroom':'红色蘑菇',
    'Red Sand':'红沙','Red Sandstone':'红砂岩','Rose Bush':'玫瑰丛','Sand':'沙子',
    'Sandstone':'砂岩','Sculk Sensor':'幽匿感测体','Sea Pickle':'海泡菜','Snow Block':'雪块',
    'Soul Sand':'灵魂沙','Sugar Cane':'甘蔗','Sulfur':'硫磺','Sulfur Spike':'硫磺尖刺',
    'Sunflower':'向日葵','TNT':'TNT','Terracotta':'陶瓦','Torchflower':'火炬花',
    'Tuff':'凝灰岩','TNT':'TNT','Warped Fungus':'诡异菌','Water Bottle':'水瓶','Wheat':'小麦',
    'Wither Rose':'凋零玫瑰','Cinnabar':'朱砂','Cinnabar Bricks':'朱砂砖',
    'Cinnabar Slab':'朱砂台阶','Chiseled Quartz Block':'雕纹石英块',
    'Copper Torch Revision 2':'铜火把','Dark Prismarine':'暗海晶石','Deepslate Bricks':'深板岩砖','Deepslate Tiles':'深板岩瓦',
    'Iron Chain':'铁链','Polished Blackstone':'磨制黑石','Polished Blackstone Slab':'磨制黑石台阶',
    'Polished Cinnabar':'磨制朱砂','Polished Tuff':'磨制凝灰岩','Red Sandstone Slab':'红砂岩台阶',
    'Resin Brick Slab':'树脂砖台阶','Sandstone Slab':'砂岩台阶','Splash Water Bottle':'喷溅水瓶',
    'Lingering Water Bottle':'滞留水瓶','Copper Spear':'铜矛','Iron Chain':'铁链',
    'Netherite Upgrade':'下界合金升级',
}

def _rule_potion(en):
    en = en.strip()
    if en in POTION_SPECIAL:
        return POTION_SPECIAL[en]
    prefix = ''; body = en
    for p, cn in [('Lingering ', '滞留型'), ('Splash ', '喷溅型')]:
        if en.startswith(p + 'Potion of '):
            prefix = cn; body = en[len(p):]; break
    if body.startswith('Potion of '):
        effect = body[len('Potion of '):]
        suffix = ''
        if effect.endswith(' Extended'):
            effect = effect[:-9]; suffix = '（延长版）'
        elif effect.endswith(' Enhanced'):
            effect = effect[:-9]; suffix = '（强化版）'
        return prefix + EFFECT.get(effect, effect) + '药水' + suffix
    return None

def _rule_tag(en):
    if not en.startswith('Any '):
        return None
    body = en[4:]
    return '任意' + TAG.get(body, body)

def _rule_trim(en):
    m = re.match(r'^(.+) Armor Trim$', en)
    if m:
        return ARMOR_TRIM.get(m.group(1), m.group(1)) + '盔甲纹饰'
    return None

def _rule_copper_stage(en):
    for stage, cn in COPPER_STAGE.items():
        if en.startswith(stage + ' '):
            rest = en[len(stage)+1:]
            if rest in COPPER_ITEM:
                return cn + '的' + COPPER_ITEM[rest]
    return None

def _rule_waxed(en):
    if en.startswith('Waxed '):
        rest = en[6:]
        rcn = cn_of(rest)
        if rcn and rcn != rest:
            return '涂蜡的' + rcn
    return None

def _rule_wood(en):
    for wood, cn in WOOD.items():
        if en == wood + ' Log': return cn + '原木'
        if en == wood + ' Planks': return cn + '木板'
        if en == wood + ' Boat': return cn + ('船' if cn.endswith('木') else '木船')
        if en == wood + ' Boat with Chest': return cn + ('运输船' if cn.endswith('木') else '木运输船')
        if en == wood + ' Stem': return cn + '菌柄'
        if en == 'Stripped ' + wood + ' Log': return '去皮' + cn + '原木'
        if en == 'Stripped ' + wood + ' Stem': return '去皮' + cn + '菌柄'
    if en == 'Bamboo Raft': return '竹筏'
    if en == 'Bamboo Raft with Chest': return '运输竹筏'
    if en == 'Bamboo Mosaic': return '竹马赛克'
    if en == 'Bamboo Slab': return '竹台阶'
    return None

def _rule_tool_armor(en):
    for mat, mcn in MAT.items():
        for t, tcn in TOOL.items():
            if en == mat + ' ' + t:
                return mcn + tcn
        for a, acn in ARMOR.items():
            if en == mat + ' ' + a:
                return mcn + acn
    return None

def _rule_color(en):
    for color, ccn in COLOR.items():
        for suf, scn in COLOR_SUFFIX.items():
            if en == color + ' ' + suf:
                return ccn + scn
    return None

def _rule_mineral(en):
    m = re.match(r'^Block of (.+)$', en)
    if m: return MAT.get(m.group(1), m.group(1)) + '块'
    m = re.match(r'^Deepslate (.+) Ore$', en)
    if m: return '深层' + MAT.get(m.group(1), m.group(1)) + '矿石'
    m = re.match(r'^Nether (.+) Ore$', en)
    if m: return '下界' + MAT.get(m.group(1), m.group(1)) + '矿石'
    m = re.match(r'^(.+) Ore$', en)
    if m: return MAT.get(m.group(1), m.group(1)) + '矿石'
    m = re.match(r'^(.+) Ingot$', en)
    if m: return MAT.get(m.group(1), m.group(1)) + '锭'
    m = re.match(r'^(.+) Nugget$', en)
    if m: return MAT.get(m.group(1), m.group(1)) + '粒'
    return None

BANNER_PAT = {'Creeper': '苦力怕', 'Flower': '花朵', 'Mojang': 'Mojang', 'Skull': '头颅'}


def _rule_arrow(en):
    m = re.match(r'^Arrow of (.+)$', en)
    if m:
        return EFFECT.get(m.group(1), m.group(1)) + '之箭'
    return None


def _rule_bundle(en):
    m = re.match(r'^(.+) Bundle$', en)
    if m:
        c = COLOR.get(m.group(1))
        return (c + '收纳袋') if c else (m.group(1) + '色收纳袋')
    return None


def _rule_banner(en):
    m = re.match(r'^(.+) Banner Pattern$', en)
    if m:
        return BANNER_PAT.get(m.group(1), m.group(1)) + '旗帜图案'
    return None


def _rule_hanging_sign(en):
    if en == 'Bamboo Hanging Sign':
        return '竹挂告示牌'
    return None


_RULES = [_rule_potion, _rule_tag, _rule_trim, _rule_copper_stage, _rule_waxed, _rule_wood, _rule_tool_armor, _rule_color, _rule_mineral, _rule_arrow, _rule_bundle, _rule_banner, _rule_hanging_sign]

def cn_of(en):
    """英文材料名 -> 中文名（含分号分隔的多种材料）"""
    if not en:
        return en
    if ';' in en:
        return '；'.join(cn_of(x.strip()) for x in en.split(';') if x.strip())
    en = en.strip()
    if en in EN2CN:
        return EN2CN[en]
    if en in BLOCK:
        return BLOCK[en]
    if en in COPPER_ITEM:
        return COPPER_ITEM[en]
    for fn in _RULES:
        r = fn(en)
        if r:
            return r
    return en


def _out_parts(output):
    """'Iron Ingot,9' -> ('铁锭', 9)"""
    if ',' in output:
        name, cnt = output.rsplit(',', 1)
        try:
            return cn_of(name), int(cnt)
        except ValueError:
            return cn_of(name), 1
    return cn_of(output), 1

def recipe_subtitle(kind, recipe):
    """生成配方字幕文字，返回 (字幕字符串, 是否含多种可替代材料)"""
    from collections import Counter
    if kind == 'crafting':
        mats = Counter(recipe.get('grid', {}).values())
        parts = [f"{cn_of(en)}x{cnt}" for en, cnt in mats.items()]
        out, ocnt = _out_parts(recipe.get('output', ''))
        out_s = out if ocnt == 1 else f"{out}x{ocnt}"
        return ' + '.join(parts) + ' → ' + out_s
    if kind == 'smelting' or kind == 'stonecutting':
        ins = [cn_of(x) for x in recipe.get('input', []) if x]
        out, ocnt = _out_parts(recipe.get('output', ''))
        out_s = out if ocnt == 1 else f"{out}x{ocnt}"
        return ' / '.join(ins) + ' → ' + out_s
    if kind == 'smithing':
        parts = [cn_of(recipe.get('template','')), cn_of(recipe.get('base','')),
                 cn_of(recipe.get('addition',''))]
        out, _ = _out_parts(recipe.get('output', ''))
        return ' + '.join(p for p in parts if p) + ' → ' + out
    if kind == 'brewing':
        ing = cn_of(recipe.get('ingredient',''))
        base = cn_of(recipe.get('base','').split(';')[0].strip())
        out = cn_of(recipe.get('output','').split(';')[0].strip())
        return f"{ing} + {base} → {out}"
    return ''

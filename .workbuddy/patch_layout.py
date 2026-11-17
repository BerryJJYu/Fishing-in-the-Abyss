# -*- coding: utf-8 -*-
# 布局重构: PC双栏一屏化 + 移动端响应式（只改 head/body，script 段原样保留）
s = open('D:/self-project/game/src/template.html', encoding='utf-8').read()

# 定位脚本段起点（第一个 <script>），脚本之后的内容原样保留
script_start = s.find('<script>\n/*__BREAK_INFINITY__*/')
assert script_start > 0, "脚本锚点未找到"
scripts_part = s[script_start:]

NEW_HEAD_BODY = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>深渊摸鱼录 · 可玩原型 v0.1</title>
<style>
  :root {
    --bg: #0d0a08; --panel: #1c1410; --panel2: #241a12;
    --parchment: #d9c79a; --parchment-dim: #a08c5f;
    --blood: #8a1a1a; --blood-bright: #c62828; --gold: #ffd700;
    --green: #3cff9e; --text: #d9c79a; --border: #3a2a1a;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
  html, body { height: 100%; }
  body { background: var(--bg); color: var(--text); font-family: "Microsoft YaHei", monospace; padding: 8px; overflow-x: hidden; }
  h1 { color: var(--blood-bright); font-size: 17px; letter-spacing: 5px; text-align: center; text-shadow: 0 0 10px #4a0000; line-height: 1.2; }
  .sub { text-align: center; color: var(--parchment-dim); font-size: 10px; margin-bottom: 6px; }
  #topbar { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-bottom: 8px; }
  #topbar .stat { min-width: 0; }
  @media (min-width: 1100px) { #topbar { grid-template-columns: repeat(6, 1fr); } }
  .stat { background: var(--panel); border: 1px solid var(--border); padding: 4px 8px; border-radius: 4px; }
  .stat .v { color: var(--gold); font-size: 13px; font-weight: bold; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .stat .k { color: var(--parchment-dim); font-size: 9px; }
  #zoneinfo .v { color: var(--blood-bright); }
  #hallBtn, #sfxBtn, #musicBtn { cursor: pointer; display: flex; align-items: center; }
  #hallBtn .v, #sfxBtn .v, #musicBtn .v { font-size: 12px; }
  canvas { display: block; width: 100%; height: auto; background: #120c08; border: 1px solid var(--border); border-radius: 4px; image-rendering: pixelated; aspect-ratio: 3 / 1; }
  #mainGrid { display: grid; grid-template-columns: minmax(0, 1fr); gap: 8px; align-items: start; }
  @media (min-width: 1100px) {
    #mainGrid { grid-template-columns: minmax(0, 1fr) 340px; }
    #colSide { display: flex; flex-direction: column; gap: 8px; }
  }
  #colMain, #colSide { min-width: 0; display: flex; flex-direction: column; gap: 8px; }
  #panel, #panel2, #panel3, #panel4 { display: flex; gap: 6px; flex-wrap: wrap; }
  .box { background: var(--panel); border: 1px solid var(--border); border-radius: 4px; padding: 6px 8px; min-width: 0; }
  .boxflex1 { flex: 1 1 200px; min-width: 0; }
  .boxtitle { color: var(--parchment-dim); font-size: 10px; margin-bottom: 4px; letter-spacing: 1px; }
  button {
    background: linear-gradient(180deg, #4a2a1a, #2a1810); color: var(--gold);
    border: 1px solid #6a4a2a; padding: 6px 10px; border-radius: 4px; cursor: pointer;
    font-family: inherit; font-size: 12px; min-height: 32px;
  }
  button:hover:not(:disabled) { background: linear-gradient(180deg, #6a3a1a, #3a2216); border-color: var(--gold); }
  button:disabled { opacity: 0.4; cursor: not-allowed; }
  #prestigeBtn {
    background: linear-gradient(180deg, #5a0a0a, #2a0505); border-color: #8a1a1a;
    color: #ff6c6c; font-weight: bold; animation: pulse 1.6s infinite; width: 100%; margin-top: 6px; min-height: 44px;
  }
  @keyframes pulse { 0%,100% { box-shadow: 0 0 4px #8a1a1a; } 50% { box-shadow: 0 0 18px #c62828; } }
  #ascendBtn {
    background: linear-gradient(180deg,#1a2a4a,#0a1428); border-color:#6c9cff;
    color:#9cc8ff; font-weight: bold; width: 100%; margin-top: 4px; min-height: 44px;
  }
  #affixList .chip { display: inline-block; margin: 3px; padding: 3px 8px; border-radius: 3px; font-size: 11px; border: 1px solid; }
  #gearList .chip { white-space: normal; line-height: 1.5; display: block; margin: 3px 0; }
  #log { height: 96px; overflow-y: auto; font-size: 10px; line-height: 1.5; color: var(--green); background: #0a0806; padding: 4px; }
  #log .ev-t2 { color: #ffd700; } #log .ev-t3 { color: #ff9e3c; } #log .ev-t4 { color: #ff3c6c; font-weight: bold; }
  .flex1 { flex: 1 1 200px; min-width: 0; }
  #objList, #expArea, #talentArea, #dpTalentArea, #chalArea { font-size: 11px; line-height: 1.7; }
  #panel2 button, #panel3 button, #panel4 button { font-size: 11px; min-height: 30px; }
  #panel2 button:disabled, #panel3 button:disabled, #panel4 button:disabled { opacity: 0.35; }
  #prestigeBtn, #ascendBtn { font-size: 12px; }
  #popup {
    position: fixed; right: 10px; bottom: 10px; width: min(300px, calc(100vw - 20px));
    background: var(--panel2); border: 1px solid var(--gold); border-radius: 6px;
    padding: 10px; font-size: 12px; box-shadow: 0 0 24px rgba(255, 215, 0, .15); z-index: 99;
  }
  #popup h3 { color: var(--gold); font-size: 12px; margin-bottom: 6px; }
  #popup .close { float: right; cursor: pointer; color: var(--parchment-dim); }
  .hidden { display: none !important; }
  #ceremony { position: fixed; inset: 0; background: rgba(0,0,0,.88); z-index: 100; display: flex; align-items: center; justify-content: center; flex-direction: column; padding: 16px; text-align: center; }
  #ceremony h2 { color: var(--blood-bright); font-size: 24px; letter-spacing: 8px; text-shadow: 0 0 20px #800; margin-bottom: 10px; }
  #ceremony p { color: var(--parchment); max-width: 480px; line-height: 1.8; margin-bottom: 16px; white-space: pre-line; }
  #hallModal { position: fixed; inset: 0; background: rgba(0,0,0,.88); z-index: 100; display: flex; align-items: center; justify-content: center; padding: 10px; }
  #hallInner { background: var(--panel2); border: 1px solid var(--gold); border-radius: 6px; padding: 14px; width: min(640px, 96vw); max-height: 88vh; overflow-y: auto; }
  #hallInner h2 { color: var(--gold); font-size: 16px; letter-spacing: 3px; margin-bottom: 4px; }
  #hallInner h3 { color: var(--parchment); font-size: 12px; margin: 10px 0 6px; }
  .ach { display: inline-block; width: 46%; min-width: 150px; margin: 3px; padding: 5px 7px; border: 1px solid var(--border); border-radius: 4px; font-size: 10px; vertical-align: top; }
  .ach.on { border-color: var(--gold); color: var(--gold); background: #2a2010; }
  .ach.off { color: #5a4a3a; }
  .ach b { display: block; font-size: 11px; }
  .tl { border-left: 3px solid var(--blood); padding: 3px 9px; margin: 5px 0; font-size: 11px; color: var(--parchment); }
  .tl small { color: var(--parchment-dim); }
  /* 竖屏手机: 进一步压缩 */
  @media (max-width: 600px) {
    body { padding: 5px; }
    h1 { font-size: 14px; letter-spacing: 3px; }
    .stat .v { font-size: 12px; }
    button { padding: 5px 8px; font-size: 11px; min-height: 36px; }
    #log { height: 80px; }
  }
</style>
</head>
<body>
<h1>深 渊 摸 鱼 录</h1>
<div class="sub">复古暗黑 · 指数爆炸 · 乐子人挂机 —— 可玩原型 v0.1（数值=设计基准，勿当最终版）</div>

<div id="topbar">
  <div class="stat"><div class="k">金币</div><div class="v" id="uiGold">0</div></div>
  <div class="stat"><div class="k">战力 DPS</div><div class="v" id="uiDps">10</div></div>
  <div class="stat" id="zoneinfo"><div class="k">当前区域</div><div class="v" id="uiZone">腐朽墓穴 · 第1区</div></div>
  <div class="stat"><div class="k">转生 / 神格</div><div class="v" id="uiPrestige">0</div></div>
  <div class="stat" style="cursor:pointer" id="hallBtn"><div class="v">🏛 成就墙 / 时间线收藏馆</div></div>
  <div class="stat" style="cursor:pointer; display:flex; gap:8px; justify-content:center" >
    <div class="v" style="cursor:pointer" id="sfxBtn">🔊 音效开</div>
    <div class="v" style="cursor:pointer" id="musicBtn">🎵 BGM关</div>
  </div>
</div>

<div id="mainGrid">
  <div id="colMain">
    <canvas id="scene" width="900" height="300"></canvas>
    <div id="panel">
      <div class="box" style="flex:0 0 220px">
        <div class="boxtitle">深 渊 升 级</div>
        <div style="font-size:10px;color:var(--parchment-dim)">攻击 <span id="uiAtk">10</span> · 攻速 ×<span id="uiSpd">1.0</span> · 暴击 <span id="uiCrit">5%</span></div>
        <div style="margin-top:4px"><button id="buyAtk">⚔攻击 Lv.<span id="uiLv">0</span> (<span id="uiCost">10</span>)</button></div>
        <div style="margin-top:3px"><button id="buySpd">⚡攻速 Lv.<span id="uiSpdLv">0</span>/15 (<span id="uiSpdCost">50</span>)</button></div>
        <div style="margin-top:3px"><button id="buyCrt">🎯暴击 Lv.<span id="uiCrtLv">0</span>/20 (<span id="uiCrtCost">100</span>)</button></div>
        <div style="margin-top:4px"><button id="buyMaxBtn" style="width:100%">一键买满（攻击线）</button></div>
        <button id="prestigeBtn" class="hidden">【掀桌子重开时间线】<br>献祭一切 → 黑魂工资 +<span id="uiSoulsGain">5</span> 点</button>
        <button id="ascendBtn" class="hidden">【飞升·面见摸鱼之神】<br>区80解锁 → 神格点 +<span id="uiDpGain">1</span> · 保留装备与天赋</button>
      </div>
      <div class="box boxflex1">
        <div class="boxtitle">深 渊 装 备 栏（GS对比 · 自动分解 · 强化绑槽）</div>
        <div id="gearList"><span style="font-size:11px;color:var(--parchment-dim)">空空如也。去打第一个 Boss（第10区）。</span></div>
      </div>
      <div class="box boxflex1">
        <div class="boxtitle">深 渊 摸 鱼 实 录</div>
        <div id="log"></div>
      </div>
    </div>
    <div id="panel2">
      <div class="box boxflex1">
        <div class="boxtitle">主 动 技 能（热键 1/2/3）—— 站桩是可耻的</div>
        <div style="display:flex; gap:5px; flex-wrap:wrap;">
          <button id="skFury">1 精神攻击 ×<span id="skFuryMult">5</span><br><span id="skFuryCd" style="font-size:10px">就绪</span></button>
          <button id="skSlam">2 掀桌一击 <span id="skSlamSec">60</span>s DPS<br><span id="skSlamCd" style="font-size:10px">就绪</span></button>
          <button id="skTax">3 收保护费 <span id="skTaxSec">90</span>s<br><span id="skTaxCd" style="font-size:10px">就绪</span></button>
          <button id="tauntBtn" class="hidden" style="background:linear-gradient(180deg,#4a0a2a,#2a0518);border-color:#c62828;color:#ff9e9e;">【嘘他！】破防×3（6s）</button>
        </div>
        <div style="margin-top:5px;display:flex;gap:5px;flex-wrap:wrap;">
          <button id="upFury" style="font-size:11px">升级精神攻击 ×2/级+1s (Lv.<span id="upFuryLv">0</span>/5 · <span id="upFuryCost">?</span>)</button>
          <button id="upSlam" style="font-size:11px">升级掀桌一击 +30s DPS (Lv.<span id="upSlamLv">0</span>/4 · <span id="upSlamCost">?</span>)</button>
          <button id="upTax" style="font-size:11px">升级收保护费 +60s (Lv.<span id="upTaxLv">0</span>/4 · <span id="upTaxCost">?</span>)</button>
        </div>
      </div>
      <div class="box boxflex1">
        <div class="boxtitle">深 渊 目 标（KPI 由魔王友情赞助）</div>
        <div id="objList"></div>
      </div>
    </div>
  </div>
  <div id="colSide">
    <div id="panel3">
      <div class="box boxflex1">
        <div class="boxtitle">铁 匠 铺（失败不降级 · 连败2次必成 · 10%暴击+2级）</div>
        <div style="font-size:10px;color:var(--parchment-dim)">碎屑：<span id="uiScrap" style="color:var(--gold)">0</span></div>
        <div style="display:flex; gap:4px; margin-top:4px; flex-wrap:wrap;">
          <button id="enhWeapon">⚔武器 Lv.<span id="enhWeaponLv">0</span>/15 (<span id="enhWeaponCost">?</span>屑+<span id="enhWeaponGold">?</span>)</button>
          <button id="enhArmor">🛡防具 Lv.<span id="enhArmorLv">0</span>/15 (<span id="enhArmorCost">?</span>屑+<span id="enhArmorGold">?</span>)</button>
          <button id="enhTrinket">💍饰品 Lv.<span id="enhTrinketLv">0</span>/15 (<span id="enhTrinketCost">?</span>屑+<span id="enhTrinketGold">?</span>)</button>
        </div>
        <div id="bsMsg" style="font-size:11px;color:var(--parchment);margin-top:4px;min-height:14px">铁匠：想强化就说话，别拿眼睛锯我。</div>
      </div>
      <div class="box boxflex1" id="dpBox">
        <div class="boxtitle">神 格 商 店（神格点：<span id="uiDp" style="color:var(--gold)">0</span> · 飞升区80解锁）</div>
        <div style="display:flex;gap:4px;flex-wrap:wrap;">
          <button id="dpMight">神威 ×10 (<span id="dpMightCost">1</span>) Lv.<span id="dpMightLv">0</span></button>
          <button id="dpHaste">神速 ×1.5 (<span id="dpHasteCost">1</span>) Lv.<span id="dpHasteLv">0</span></button>
          <button id="dpTouch">神触 ×3 (<span id="dpTouchCost">1</span>) Lv.<span id="dpTouchLv">0</span></button>
        </div>
        <div style="font-size:10px;color:var(--parchment-dim);margin-top:3px">飞升保留：装备/强化/天赋/商店/成就。清空：区域/等级/金币。</div>
        <div class="boxtitle" style="margin-top:6px">神 格 天 赋 树</div>
        <div id="dpTalentArea"></div>
        <div class="boxtitle" style="margin-top:6px">周 目 挑 战（本周期内飞升即达成）</div>
        <div id="chalArea"></div>
      </div>
    </div>
    <div id="panel4">
      <div class="box boxflex1">
        <div class="boxtitle">骷 髅 远 征 队（主动派遣 · 5分钟 · 派出去的兵不会摸鱼）</div>
        <div id="expArea"></div>
      </div>
    </div>
  </div>
</div>

<div id="popup" class="hidden">
  <span class="close" onclick="this.parentElement.classList.add('hidden')">[关闭]</span>
  <h3 id="popupTitle"></h3>
  <div id="popupBody"></div>
</div>

<div id="ceremony" class="hidden">
  <h2>时 间 线 已 掀 翻</h2>
  <p id="ceremonyText"></p>
  <button id="ceremonyOk">接受这一切，继续摸鱼</button>
</div>

<div id="hallModal" class="hidden">
  <div id="hallInner">
    <h2>成 就 墙 · 时 间 线 收 藏 馆</h2>
    <div style="font-size:11px;color:var(--parchment-dim)">每枚成就：黑魂工资 +1 点 + 永久全局 ×1.05。魔王说这叫员工激励，虽然他没发过工资。</div>
    <div id="achSummary" style="font-size:12px;color:var(--gold);margin-top:6px"></div>
    <h3>💀 Boss 图 鉴（物理超度花名册）</h3>
    <div id="dexGrid"></div>
    <h3>🏆 成 就 墙</h3>
    <div id="achGrid"></div>
    <h3>🕰 时 间 线 收 藏 馆（被你掀掉的时间线）</h3>
    <div id="tlList"></div>
    <div style="text-align:center;margin-top:10px"><button id="hallClose">关闭并继续摸鱼</button></div>
  </div>
</div>

'''

NEW_HEAD_BODY += scripts_part
open('D:/self-project/game/src/template.html', 'w', encoding='utf-8').write(NEW_HEAD_BODY)
print("布局重构完成（写盘核验: viewport=%s mainGrid=%s 脚本保留=%s)" % (
  'viewport' in NEW_HEAD_BODY, 'mainGrid' in NEW_HEAD_BODY, '/*__BREAK_INFINITY__*/' in NEW_HEAD_BODY))

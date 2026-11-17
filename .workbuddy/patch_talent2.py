# -*- coding: utf-8 -*-
# v7 天赋树第二批: 渲染/存档v6/仪式重置
s = open('D:/self-project/game/src/template.html', encoding='utf-8').read()

# ===== refreshUI: 天赋区渲染（插在 shopBtns 循环后） =====
old = """  for (const [btn, k] of Object.entries(shopBtns)) {
    const lv = S.shop[k], cost = ECON.shopCost(lv);
    $(btn + 'Lv').textContent = lv; $(btn + 'Cost').textContent = cost;
    $(btn).disabled = S.souls < cost;
  }"""
new = """  for (const [btn, k] of Object.entries(shopBtns)) {
    const lv = S.shop[k], cost = ECON.shopCost(lv);
    $(btn + 'Lv').textContent = lv; $(btn + 'Cost').textContent = cost;
    $(btn).disabled = S.souls < cost;
  }
  // 天赋树渲染
  const lineNames = { tyr: '暴政', sqz: '压榨', mad: '发疯' };
  const ta = document.getElementById('talentArea');
  ta.innerHTML = TALENTS.map(t => {
    const owned = hasTalent(t.id);
    const lineOk = S.shop[t.line] >= t.needLv;
    const afford = S.souls >= t.cost;
    const cls = owned ? 'color:var(--green)' : lineOk ? 'color:var(--gold)' : 'color:var(--parchment-dim)';
    const btn = owned ? ' <b>✓已点亮</b>'
      : `<button data-tal="${t.id}" style="font-size:10px;padding:2px 8px" ${(!lineOk || !afford) ? 'disabled' : ''}>点亮 (${t.cost}点)</button>`;
    const lock = !lineOk ? `<small>需${lineNames[t.line]}线 Lv.${t.needLv}</small> ` : '';
    return `<div style="margin-bottom:3px"><span style="${cls}">${owned ? '★' : '☆'} ${t.name}</span> <small>${t.desc}</small> ${lock}${btn}</div>`;
  }).join('');"""
assert old in s, "render"; s = s.replace(old, new)

# ===== save v6 =====
old = """    v: 5, gold: S.gold.toString(), zone: S.zone, level: S.level, prestige: S.prestige,
    spd: S.spd, crt: S.crt, souls: S.souls, shop: S.shop, maxZone: S.maxZone, allMax: S.allMax,
    skillLv: S.skillLv, stats: S.stats, achievements: S.achievements, timeline: S.timeline,
    gear: S.gear, enh: S.enh, pity: S.pity, scrap: S.scrap,
    buffs: S.buffs, lastSave: Date.now(),"""
new = """    v: 6, gold: S.gold.toString(), zone: S.zone, level: S.level, prestige: S.prestige,
    spd: S.spd, crt: S.crt, souls: S.souls, shop: S.shop, maxZone: S.maxZone, allMax: S.allMax,
    skillLv: S.skillLv, stats: S.stats, achievements: S.achievements, timeline: S.timeline,
    gear: S.gear, enh: S.enh, pity: S.pity, scrap: S.scrap, talents: S.talents,
    buffs: S.buffs, lastSave: Date.now(),"""
assert old in s, "save"; s = s.replace(old, new)

old = """        if (d.v >= 5) {
          S.gear = d.gear || S.gear; S.enh = d.enh || S.enh; S.pity = d.pity || S.pity; S.scrap = d.scrap || 0;
        } else {"""
new = """        if (d.v >= 5) {
          S.gear = d.gear || S.gear; S.enh = d.enh || S.enh; S.pity = d.pity || S.pity; S.scrap = d.scrap || 0;
          if (d.v >= 6) S.talents = d.talents || {};
        } else {"""
assert old in s, "load"; s = s.replace(old, new)

# ===== softReset: 天赋保留（转生不清天赋，只清需消耗的部分） =====
# softReset 不动 S.talents —— 现有代码不重置它，无需改
open('D:/self-project/game/src/template.html', 'w', encoding='utf-8').write(s)
print("天赋树第二批完成")

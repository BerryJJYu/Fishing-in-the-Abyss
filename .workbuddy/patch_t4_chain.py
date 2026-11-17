# -*- coding: utf-8 -*-
# 任务4: 链式奇遇 + 每日魔王晨会
s = open('D:/self-project/game/src/template.html', encoding='utf-8').read()

# ===== State =====
old = """  exp: { '033': null, '077': null, '999': null },"""
new = """  exp: { '033': null, '077': null, '999': null },
  morningDate: '', chainQueue: null,"""
assert old in s, "state"; s = s.replace(old, new)

# ===== 链式奇遇定义 + 晨会（插在远征逻辑后） =====
old = """// ===== 成就墙 ====="""
new = """// ===== 链式奇遇（部分事件结算后 40 秒触发后续） =====
const CHAIN_EVENTS = {
  evt_card_night: [
    { kind: 'gamble', chance: 0.5,
      win: { kind: 'goldMult', mult: 25, log: '第二轮：哥布林亮出四条K，但你亮出了王（ literally 一张画着魔王的牌）。裁判判定：魔王最大。' },
      lose: { kind: 'goldMult', mult: 2, log: '第二轮输了，但哥布林讲义气，只收了茶水费。' } },
    { text: '深夜约战', dur: 0 },
  ],
  evt_altar_snack: [
    { kind: 'buff', zone: 'allDmg', mult: 20, durationSec: 300,
      log: '后续：魔王发现贡品被啃了一口，全矿场紧急排查。你在恐惧中觉醒——全乘区 ×20（5分钟）。' },
    { text: '魔王排查', dur: 0 },
  ],
  evt_demon_team_building: [
    { kind: 'goldMult', mult: 40,
      log: '后续：团建横幅披风照片流出，深渊网友狂点赞，魔工坊连夜推出同款周边卖爆。' },
    { text: '周边爆卖', dur: 0 },
  ],
};
function queueChain(srcId) {
  const ch = CHAIN_EVENTS[srcId];
  if (!ch || Math.random() > 0.5) return;
  S.chainQueue = { srcId, at: Date.now() + 40000 };
  addLog('[预兆] 你有种奇怪的预感：这件事……还没完。', '');
}
function settleChain() {
  const q = S.chainQueue;
  S.chainQueue = null;
  const ch = (CHAIN_EVENTS[q.srcId] || [])[0];
  if (!ch) return;
  const m = mults();
  let outcome;
  if (ch.kind === 'gamble') {
    const win = Math.random() < ch.chance;
    (win ? SFX.gambleWin() : SFX.gambleLose());
    outcome = applyEventEffect(win ? ch.win : ch.lose, '链式' + (win ? '赌赢' : '赌输'));
  } else {
    outcome = applyEventEffect(ch, '链式');
  }
  showPopup('【链式奇遇】', ['上一件事的余波来了——', '→ ' + outcome], 'ev-t3');
}

// ===== 每日魔王晨会 =====
function checkMorning() {
  const today = new Date().toDateString();
  if (S.morningDate === today) return;
  S.morningDate = today;
  S.souls += 1;
  const buffPool = [
    { zone: 'atk', mult: 100, dur: 1800, txt: '魔王念昨日KPI时慷慨激昂，全员攻击 ×100（30分钟）' },
    { zone: 'goldGain', mult: 100, dur: 1800, txt: '晨会宣布本周血祭KPI超额，金币 ×100（30分钟）' },
    { zone: 'atkSpeed', mult: 30, dur: 1800, txt: '魔王迟到15分钟，会议提前结束，全员攻速 ×30（30分钟）' },
  ];
  const b = buffPool[Math.floor(Math.random() * buffPool.length)];
  S.buffs.push({ zone: b.zone, mult: b.mult, until: Date.now() + b.dur * 1000 });
  showPopup('【每日魔王晨会】签到', [
    '魔王的晨会语录（今日随机一条）：',
    '"他卷任他卷，深渊我垫底。散会。"',
    '签到奖励：黑魂工资 +1 点 + ' + b.txt,
  ], 'ev-t3');
  addLog('[晨会] 每日签到完成：黑魂 +1，' + b.txt, 'ev-t3');
  SFX.claim();
  save();
}

// ===== 成就墙 ====="""
assert old in s, "chain"; s = s.replace(old, new)

# ===== fireEvent 结算后入链队 + tick 触发 + 晨会检查 =====
old = """  const rw = ev.reward;
  const result = applyEventEffect(rw, '自动');
  showPopup(title, body.concat(['→ ' + result]), 'ev-t' + ev.tier.slice(1));
}"""
new = """  const rw = ev.reward;
  const result = applyEventEffect(rw, '自动');
  queueChain(ev.id);
  showPopup(title, body.concat(['→ ' + result]), 'ev-t' + ev.tier.slice(1));
}"""
assert old in s, "firechain"; s = s.replace(old, new)

old = """    showPopup(title + ' · 你来决策', body, 'ev-t' + ev.tier.slice(1), {
      sticky: true,
      buttons: chs.map((c, i) => ({
        label: (['A: ', 'B: ', 'C: '][i] || '') + c.text,
        cb: () => resolveChoice({ choices: chs, tier: ev.tier }, i),
      })),
    });
    return;"""
new = """    showPopup(title + ' · 你来决策', body, 'ev-t' + ev.tier.slice(1), {
      sticky: true,
      buttons: chs.map((c, i) => ({
        label: (['A: ', 'B: ', 'C: '][i] || '') + c.text,
        cb: () => { resolveChoice({ choices: chs, tier: ev.tier }, i); queueChain(ev.id); },
      })),
    });
    return;"""
assert old in s, "choicechain"; s = s.replace(old, new)

old = """  // 选项事件挂起中：15秒未决策自动执行第一项（深渊不等人）"""
new = """  // 链式奇遇到期
  if (S.chainQueue && Date.now() - S.chainQueue.at >= 40000) settleChain();
  // 每日晨会（每分钟检查一次即可，借 achTimer）
  // 选项事件挂起中：15秒未决策自动执行第一项（深渊不等人）"""
assert old in s, "tickchain"; s = s.replace(old, new)

old = """  if (achTimer >= 1) { achTimer = 0; checkAchievements(); checkGlitchReroll(); }"""
new = """  if (achTimer >= 1) { achTimer = 0; checkAchievements(); checkGlitchReroll(); checkMorning(); }"""
assert old in s, "morning"; s = s.replace(old, new)

# ===== save v8 字段 =====
old = """    exp: S.exp,
    buffs: S.buffs, lastSave: Date.now(),"""
new = """    exp: S.exp, morningDate: S.morningDate,
    buffs: S.buffs, lastSave: Date.now(),"""
assert old in s, "save"; s = s.replace(old, new)
old = """            if (d.v >= 8) { S.dp = d.dp || 0; S.dpShop = d.dpShop || { might: 0, haste: 0, touch: 0 }; S.exp = d.exp || S.exp; }"""
new = """            if (d.v >= 8) { S.dp = d.dp || 0; S.dpShop = d.dpShop || { might: 0, haste: 0, touch: 0 }; S.exp = d.exp || S.exp; S.morningDate = d.morningDate || ''; }"""
assert old in s, "load"; s = s.replace(old, new)

open('D:/self-project/game/src/template.html', 'w', encoding='utf-8').write(s)
print("任务4补丁完成（写盘核验: chain=%s morning=%s)" % ('CHAIN_EVENTS' in s, 'checkMorning' in s))

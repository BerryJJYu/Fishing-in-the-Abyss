/* 深渊摸鱼录 - 核心数值模型(ECON)
 * 纯逻辑层：无 DOM 依赖。同一份代码进单文件 HTML 与 Node 无头仿真。
 * 对齐文档：步骤1(公式与常数) + 步骤2(zone 枚举契约)
 */
(function (root) {
  'use strict';

  const CONFIG = {
    // 玩家（步骤1 §2.3 基准常数）
    baseAtk: 10, atkGrowth: 1.15,
    baseCost: 10, costGrowth: 1.14,
    atkSpeed: 1, critChance: 0.05, critMult: 2,
    // 怪物
    baseHP: 12, hpGrowth: 1.75,   // 1.75: 装备系统上线后补偿免费成长源 r_gear≈0.044/区（原1.65墙被穿）
    baseGold: 12, goldGrowth: 1.55,
    bossEvery: 10, bossHpMult: 6, bossHpCycle: 1.75,   // 1.75: 同上补偿
    bossGoldMult: 24, bossGoldCycle: 1.5,
    // 被动收入：默认关闭(passiveRate=0)。
    // 仿真实证：任何稳态被动收入都会填补Boss战收入真空，导致墙点机制彻底失效(墙=收入真空+圈次跳变)。
    // 如后期要加"捡垃圾小鬼"，必须做成一次性/衰减型收益，不得做成比例型持续收入。
    passiveRate: 0,
    // 转生与离线
    prestigeReqZone: 50,
    // 扩展养成（有界系统：等级封顶 → 乘区有上界，保证墙力不被打破）
    spdMax: 15, spdBase: 50, spdGrowth: 2.2, spdGain: 1.08,   // 攻速线: 上限 1.08^15≈×3.17
    crtMax: 20, crtBase: 100, crtGrowth: 2.0, crtCRate: 0.015, crtCDmg: 0.1, crtCap: 0.6, // 暴击线
    // 转生商店（掀桌子赚黑魂工资，投资三线）
    shopTyrannyMult: 2.5, shopSqueezeMult: 2, shopMadnessMult: 1.5,
    comboWindowMs: 2500, comboStep: 0.05, comboCap: 3,
    // 技能升级线（金币购买，花费锚定区金币自动跟随经济膨胀）
    skillMaxFury: 5, skillMaxSlam: 4, skillMaxTax: 4,
    furyMult0: 5, furyMultStep: 2, furyDur0: 8, furyDurStep: 1,
    slamSec0: 60, slamSecStep: 30,
    taxSec0: 90, taxSecStep: 60,
    offlineRate: 0.5, offlineCapSec: 8 * 3600,
    // 事件
    eventBaseIntervalSec: 45,
  };

  const MAP_NAMES = [
    [1, 10, '腐朽墓穴 · 新手坟场'],
    [11, 20, '鲜血大教堂'],
    [21, 30, '深渊矿场'],
    [31, 40, '万魔殿 · 会议室'],
    [41, 50, '天使之门 · 客服中心'],
    [51, Infinity, '神座 · 摸鱼间'],
  ];

  const BOSS_NAMES = [
    '加班史莱姆', '堕落的天启之焰审判者·终焉形态', '血钟看守者', '万魔殿PPT魔导书·路西法监制版',
    '矿场工头·哥布林包工头', '深渊颂歌者·其名超乎想象地长到离谱',
    '客服天使·亲亲这边建议您毁灭呢', '魔王(实习期)',
  ];

  // ---------- 大数格式化 ----------
  const LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  function tierName(t) { // t>=5: AA, AB, ... AZ, BA ...
    const i = t - 5;
    return LETTERS[Math.floor(i / 26)] + LETTERS[i % 26];
  }
  function fmt(d) {
    if (d === undefined || d === null || d !== d) return '0';
    const D = root.Decimal;
    if (!(d instanceof D)) d = new D(d);
    if (!isFinite(d.mantissa) && d.exponent >= 9e15) return '∞';
    if (d.exponent < 0 || d.lt(1)) return d.toNumber().toFixed(2);
    if (d.lt(1000)) return d.toNumber().toFixed(d.lt(10) ? 2 : 1);
    const e = d.exponent, m = d.mantissa;
    const t = Math.floor(e / 3);
    const lead = m * Math.pow(10, e - t * 3);
    if (t < 5) return lead.toFixed(2) + ['', 'K', 'M', 'B', 'T'][t];
    return lead.toFixed(2) + tierName(t);
  }

  // ---------- 怪物与经济 ----------
  function isBoss(n) { return n % CONFIG.bossEvery === 0; }
  function bossCycle(n) { return Math.floor((n - 1) / CONFIG.bossEvery); }
  function bossName(n) { return BOSS_NAMES[bossCycle(n) % BOSS_NAMES.length]; }
  function mapName(n) {
    for (const [a, b, name] of MAP_NAMES) if (n >= a && n <= b) return name;
    return '???';
  }
  function zoneHP(n) {
    let hp = new Decimal(CONFIG.baseHP).times(Decimal.pow(CONFIG.hpGrowth, n - 1));
    if (isBoss(n)) hp = hp.times(CONFIG.bossHpMult).times(Decimal.pow(CONFIG.bossHpCycle, bossCycle(n)));
    return hp;
  }
  function passiveGold(n) {
    return new Decimal(CONFIG.baseGold).times(Decimal.pow(CONFIG.goldGrowth, n - 1));
  }
  function zoneGold(n) {
    let g = new Decimal(CONFIG.baseGold).times(Decimal.pow(CONFIG.goldGrowth, n - 1));
    if (isBoss(n)) g = g.times(CONFIG.bossGoldMult).times(Decimal.pow(CONFIG.bossGoldCycle, bossCycle(n)));
    return g;
  }
  function atkOf(level) {
    return new Decimal(CONFIG.baseAtk).times(Decimal.pow(CONFIG.atkGrowth, level));
  }
  function costOf(level) {
    return new Decimal(CONFIG.baseCost).times(Decimal.pow(CONFIG.costGrowth, level));
  }

  // ---------- 乘区聚合（契约见 步骤2 zones） ----------
  // affixData: {affixes:[{id, effects:[...]}], ...}
  // 返回各 zone 的总乘率；boss 上下文用于 conditional 谓词
  function computeMults(ownedAffixIds, affixTable, boss, activeBuffs, prestigeMult, now, extra) {
    const m = { atk: 1, atkSpeed: 1, critChance: 1, critMult: 1, allDmg: 1, goldGain: 1, offlineGain: 1, bossDmg: 1, eventRate: 1, moodGain: 1 };
    let global = 1;
    const byId = {}; affixTable.affixes.forEach(a => byId[a.id] = a);
    for (const id of ownedAffixIds) {
      const a = byId[id]; if (!a) continue;
      for (const e of a.effects) {
        if (e.type === 'always') { m[e.zone] *= e.mult; }
        else if (e.type === 'conditional') {
          const c = e.condition || {};
          if (c.bossNameMinLength && (!boss || boss.length < c.bossNameMinLength)) continue;
          m[e.zone] *= e.mult;
        }
      }
    }
    for (const b of (activeBuffs || [])) {
      if (b.kind === 'global') { if (b.until === 0 || now < b.until) global *= b.mult; }
      else if (b.until === 0 || now < b.until) m[b.zone] *= b.mult;
    }
    for (const k in m) m[k] *= global;
    m.allDmg *= prestigeMult;
    if (extra && extra.spdLv) m.atkSpeed *= Math.pow(CONFIG.spdGain, Math.min(extra.spdLv, CONFIG.spdMax));
    // 装备系统：always/conditional 由 computeMults 消费，proc 由应用层战斗结算消费
    if (extra && extra.gearEffects) {
      for (const e of extra.gearEffects) {
        if (e.type === 'always') m[e.zone] *= e.mult;
        else if (e.type === 'conditional') {
          const c = e.condition || {};
          if (c.bossNameMinLength && (!boss || boss.length < c.bossNameMinLength)) continue;
          m[e.zone] *= e.mult;
        }
      }
    }
    return m;
  }

  // 暴击参数（暴击线等级 → 实际暴击率/暴伤，含封顶）
  function critParams(crtLv) {
    crtLv = crtLv || 0;
    return {
      rate: Math.min(CONFIG.crtCap, CONFIG.critChance + CONFIG.crtCRate * crtLv),
      mult: CONFIG.critMult + CONFIG.crtCDmg * crtLv,
    };
  }
  // 升级线花费
  function spdCost(lv) { return new Decimal(CONFIG.spdBase).times(Decimal.pow(CONFIG.spdGrowth, Math.min(lv, CONFIG.spdMax))); }
  function crtCost(lv) { return new Decimal(CONFIG.crtBase).times(Decimal.pow(CONFIG.crtGrowth, Math.min(lv, CONFIG.crtMax))); }
  // 转生商店
  function prestigeSouls(maxZone) { return Math.floor(maxZone / 10); }
  function shopCost(lv) { return lv + 1; }
  // 技能升级: 花费锚定"区18+9lv"的金币量级，自动跟随经济膨胀
  function skillCost(lv) { return zoneGold(18 + lv * 9); }
  const SKILL_MAX = { fury: CONFIG.skillMaxFury, slam: CONFIG.skillMaxSlam, tax: CONFIG.skillMaxTax };
  function skillParams(id, lv) {
    lv = lv || 0;
    if (id === 'fury') return { mult: CONFIG.furyMult0 + CONFIG.furyMultStep * lv, dur: CONFIG.furyDur0 + CONFIG.furyDurStep * lv };
    if (id === 'slam') return { dpsSec: CONFIG.slamSec0 + CONFIG.slamSecStep * lv };
    return { goldSec: CONFIG.taxSec0 + CONFIG.taxSecStep * lv };
  }

  // 一次打击的实际伤害（crtP 可选：暴击线参数）
  function strikeDamage(atkBase, mults, rng, crtP) {
    const cp = crtP || critParams(0);
    const atk = atkBase.times(mults.atk).times(mults.allDmg);
    const cc = Math.min(1, cp.rate * mults.critChance);
    const crit = (rng || Math.random)() < cc;
    const dmg = atk.times(crit ? cp.mult * mults.critMult : 1);
    return { dmg, crit };
  }

  // DPS（离线结算与战力显示）
  function dpsOf(atkBase, mults, crtP) {
    const cp = crtP || critParams(0);
    const cc = Math.min(1, cp.rate * mults.critChance);
    return atkBase.times(mults.atk).times(mults.allDmg)
      .times(CONFIG.atkSpeed * mults.atkSpeed)
      .times(1 + cc * (cp.mult * mults.critMult - 1));
  }

  // ---------- 事件池 ----------
  function pickTier(tiers, rng) {
    const r = (rng || Math.random)() * 100;
    let acc = 0;
    for (const t of tiers) { acc += t.weight; if (r < acc) return t; }
    return tiers[tiers.length - 1];
  }
  function pickEvent(eventTable, rng) {
    const tier = pickTier(eventTable.tiers, rng);
    const pool = eventTable.events.filter(e => e.tier === tier.id);
    return pool[Math.floor((rng || Math.random)() * pool.length)] || eventTable.events[0];
  }

  // ---------- 离线快进（按击杀事件结算，非逐 tick） ----------
  // 返回 {goldGained, zonesCleared, secondsUsed}
  function simulateOffline(state, affixTable, seconds, now, squeezeMult) {
    const cap = Math.min(seconds, CONFIG.offlineCapSec);
    let t = 0, zones = 0, gold = new Decimal(0);
    const mults = computeMults(state.affixes, affixTable, null, state.buffs, state.prestigeMult, now);
    const dps = dpsOf(atkOf(state.level), mults).times(mults.offlineGain);
    let guard = 0;
    while (t < cap && guard++ < 20000) {
      const hp = zoneHP(state.zone);
      const kt = Math.max(0.05, hp.div(dps).toNumber() / CONFIG.offlineRate);
      if (kt > cap - t) break;
      t += kt;
      gold = gold.plus(zoneGold(state.zone).times(mults.goldGain).times(CONFIG.offlineRate).times(squeezeMult || 1));
      state.zone += 1; zones++;
    }
    state.gold = state.gold.plus(gold);
    return { goldGained: gold, zonesCleared: zones, secondsUsed: t };
  }

  const api = { CONFIG, passiveGold, MAP_NAMES, BOSS_NAMES, fmt, isBoss, bossCycle, bossName, mapName, zoneHP, zoneGold, atkOf, costOf, computeMults, strikeDamage, dpsOf, pickEvent, simulateOffline, tierName, critParams, spdCost, crtCost, prestigeSouls, shopCost, skillCost, SKILL_MAX, skillParams };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.ECON = api;
})(typeof window !== 'undefined' ? window : globalThis);

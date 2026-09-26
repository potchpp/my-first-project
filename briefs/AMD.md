---
ticker: AMD
company: Advanced Micro Devices
updated: 2026-09-26
type: stock-brief
shared_driver: ai-capex
---

# AMD — Advanced Micro Devices
**Date:** 2026-09-26 | *Refresh via /deep — debate round, valuation verdict in standard form, variant perception, damage-tagged kill conditions. Price $630.63 (Yahoo, 2026-09-26). Not held — surfaced by `scripts/undercover.py` (named in research of 5 holdings: MSFT, MU, NVDA, ORCL, TSM)*

**Source docs:** [[sources/AMD/10-k-fy2025]] · [[sources/AMD/q2-2026-call]]

---

## Company Snapshot

AMD ออกแบบ chip แบบ fabless (ผลิตที่ [[TSM]]) — server CPU (EPYC), AI accelerator (Instinct MI350/MI450) และ rack-scale system (Helios) ให้ hyperscaler และ AI lab รวมถึง PC CPU และ console chip Data Center เป็น 58% ของรายได้แล้ว และเป็นทางเลือกที่สองหลักของตลาด AI accelerator ที่ [[NVDA]] ครอง ~81% *(earnings agent, q2-2026-call l.14; sentiment agent)*

## Fundamentals Signal

- **Revenue durability: อ่อน** — ลูกค้าจำนวนน้อยเป็นสัดส่วนใหญ่ของรายได้ (10-K l.534); ไม่มีสัญญาซื้อระยะยาว, ยกเลิก order ได้ถ้าแจ้งก่อนส่ง >30 วัน (10-K l.622) *(fundamentals agent)*
- **Margin trend: ดีขึ้น** — GM 50% ใน FY2025 จาก 49% (10-K l.676); Q2 2026 ขึ้นเป็น 56% จาก mix ของ data center *(fundamentals + earnings agents)*
- **Capital allocation: reinvest** — ซื้อ ZT Systems $3.2B (10-K l.694), buyback $1.3B, ไม่มีปันผล *(fundamentals agent)*

## Latest Earnings — Q2 2026

- Revenue **$11.5B (+50%)**; non-GAAP EPS $1.66 (+82%); GM 56%; operating margin 27% *(q2-2026-call l.10-26)*
- Data Center **$6.7B (มากกว่า 2 เท่า YoY)** = 58% ของรายได้; server CPU สถิติใหม่ 5 ไตรมาสติด; Instinct มากกว่า 2 เท่า *(l.14-16, verified)*
- Client $3.1B (+23%), Gaming $779M (−31%), Embedded $977M (+19%)
- Q3 guide $13B ±$0.3B (+41%); **2027 Data Center คาดโตมากกว่า 2 เท่า** (l.40, verified); คาดว่าจะเกินเป้า EPS $20 และเป้าโต 35% อย่างมีนัย (l.50, verified); Anthropic 2GW MI450 เริ่ม H1 2027 (l.52)

## Bull / Bear

**Bull** *(bull_researcher)*
- **Scale economies กำลังเกิด:** Data Center +107% ขณะ GM ขึ้น 200bps — โตแล้ว margin ดีขึ้น ไม่ใช่ซื้อ share ด้วยราคา *(earnings agent l.10-34)*
- **Hyperscaler ต้องการผู้ขายรายที่สองจริง:** OpenAI 6GW + Anthropic 2GW คือการกระจายความเสี่ยงเชิงโครงสร้างของลูกค้า ไม่ใช่ macro *(earnings + sentiment agents)*
- **CPU เป็นเครื่องยนต์ที่สอง:** agentic AI ทำให้ server CPU โต >70% — ไม่ต้องชนะ NVIDIA ใน GPU ก็โตได้ *(earnings agent l.42)*

**Bear** *(bear_researcher)*
- **Backlog เป็น option ของลูกค้า ไม่ใช่ข้อผูกพันของ AMD:** ไม่มีสัญญาระยะยาว ยกเลิกได้ใน 30 วัน (10-K l.534, 622) — ตัวเลข "2027 มากกว่า 2 เท่า" ทั้งหมดตั้งอยู่บนความสัมพันธ์ที่ไม่ผูกมัด — **bear point ที่ไม่มี bull counter**
- **ราคาแซงเป้านักวิเคราะห์แล้ว:** ราคา $630 เหนือ average PT $616.51, หุ้นขึ้น ~170% YTD, market cap ใกล้ $1T *(sentiment agent)*
- **OpenAI warrant ผูกกับราคาหุ้น $600:** ความสัมพันธ์ที่ต้องให้หุ้นขึ้นก่อนถึงจะสมบูรณ์เป็นเหตุผลวนกลับ *(sentiment agent)*

## Valuation

*Lens: forward P/E เทียบกับเป้า EPS ของผู้บริหาร (valuation agent)*

ราคา $630.63 ≈ 31.5x เป้า EPS $20 ของผู้บริหาร — ต้องให้ EPS โตจาก run-rate ~$6.64 เป็น $20 (~85-90% ต่อปี) ซึ่งเป็นการต่อ trend ที่เห็นแล้ว (Data Center 2 เท่าใน 2026 และ guide 2 เท่าอีกใน 2027)

**Verdict: Deserved**

**Falsifying number:** Data Center growth ต่ำกว่า ~70% YoY ในไตรมาสใดของปี 2027

*Integrator note:* verdict นี้ขัดกับ run วันที่ 2026-09-22 ที่ ~$618 ซึ่งใช้ consensus forward P/E 55.6 และสรุปว่า "fair-to-stretched" ความต่างทั้งหมดอยู่ที่ฐาน EPS — วันนี้ใช้เป้า $20 ของผู้บริหาร ซึ่งยังไม่เกิดขึ้น ถ้าใช้ consensus แทน ตัวเลขใกล้ "Ahead of itself" มากกว่า ถือ verdict นี้ว่าบางที่สุดใน batch

## Variant Perception

- *Thesis metric:* **Data Center revenue growth YoY** (ตอนนี้ >100%) — ต้องไม่ต่ำกว่า ~70% ตลอดปี 2027
- *Where we differ from consensus:* nothing — we hold the consensus view หุ้นอยู่เหนือเป้าเฉลี่ยของนักวิเคราะห์แล้ว จึงไม่มี expectation gap ให้เก็บ

## Kill Conditions

- **Data Center growth ต่ำกว่า path ที่ guide ไว้ (~80%) และผู้บริหารถอยคำว่า "2027 more than doubles"** — ทั้ง bull และ bear ชี้มาที่จุดเดียวกัน `[bounded ~50%]`
- **Hyperscaler รายใดรายหนึ่ง (OpenAI / [[META]] / [[ORCL]] / [[MSFT]] / Anthropic) ลด capacity ที่ commit ไว้ — ไม่ใช่แค่ชะลอ** `[bounded ~40%]`
- **Helios / MI450 ramp ล่าช้าเกิน Q4 2026 หรือ MI500 เลื่อนออกจากปี 2027** `[bounded ~30%]`
- **FCF margin ไม่ขยับเกิน 20% ขณะที่ Data Center เป็น >60% ของรายได้** — scale economies ไม่เกิดจริง `[bounded ~30%]`

## What to Ask

1. **OpenAI 6GW และ Anthropic 2GW มีส่วนไหนเป็น take-or-pay?** ถ้าไม่มีเลย backlog ทั้งหมดคือ option ของลูกค้า
2. **Server CPU >70% มาจาก agentic AI จริง หรือจาก [[INTC]] เสียส่วนแบ่ง?** ถ้าเป็นอย่างหลัง growth จะหมดเมื่อ share นิ่ง
3. **Capacity ที่ [[TSM]] (N2, CoWoS) จอง AMD ได้เท่าไหร่เทียบกับ [[NVDA]] ที่จองไว้ ~60% ของ CoWoS?** supply อาจเป็นเพดานก่อน demand

---

*ไม่ใช่คำแนะนำการลงทุน — research summary จาก 10-K FY2025, Q2 2026 call และ agent analysis*

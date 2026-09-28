---
ticker: ASML
company: ASML Holding N.V.
updated: 2026-09-26
type: stock-brief
shared_driver: ai-capex
---

# ASML — ASML Holding N.V.
**Date:** 2026-09-26 | *Refresh of the 2026-09-18 brief via /deep — adds Q2 2026 call, debate round, valuation verdict, variant perception, damage-tagged kill conditions. Price $1,743.94 (yfinance, 2026-09-26; a separate web source found $1,709.64 on 2026-09-24 — small discrepancy, yfinance used as primary)*

**Source docs:** [[sources/ASML/q2-2026-call]]

> ⚠️ **Data limitation:** ASML files Form 20-F as a Dutch foreign private issuer, not a 10-K — the project's fetch script only pulls 10-Ks, so there is no local annual filing. The only local source is the Q2 FY2026 earnings call transcript (`sources/ASML/q2-2026-call.md`), cited with line numbers below. Every FY2025 annual figure and every competitive/regulatory claim below comes from the sentiment agent's web research and is marked **UNVERIFIED (web)** — treat these as directionally useful, not filing-grade.

---

## Company Snapshot

ASML เป็น **sole global supplier ของ EUV lithography machine** — คู่แข่งที่มี offering ใกล้เคียง (Nikon, Canon) ไม่มี High-NA EUV capability เลย ลูกค้าที่ใช้ leading-edge EUV ได้มีแค่ TSM ([[TSM]]), Samsung, INTC ([[INTC]]) ฝั่ง logic และ SK Hynix, MU ([[MU]])/Kioxia ฝั่ง memory *(fundamentals agent)*

จุดเปลี่ยนสำคัญของไตรมาสนี้: **High-NA EUV เข้าสู่ production จริงเป็นครั้งแรก** — Intel Foundry ใช้ผลิต Core Ultra Series 3 บน node 18A *(q2-2026-call.md l.60, 124, verified)* ส่วน **China revenue share กำลังลดจาก 33% ของ FY2025 (UNVERIFIED, web) → ~20% ของ FY2026 guidance** *(q2-2026-call.md l.48, verified)* ท่ามกลาง US bill ใหม่ (MATCH Act) ที่ขู่ขยาย export control จาก EUV ไปครอบคลุม DUV ทั้งหมด *(sentiment agent, UNVERIFIED)*

---

## Fundamentals Signal
*Source: fundamentals agent — working from q2-2026-call.md (verified, cited) + general/web knowledge for FY2025 annuals (UNVERIFIED)*

- **Revenue durability: สูงแต่ concentrate สูงเช่นเดิม** — 2027 Low-NA EUV order coverage "close to fully covered" และมี 2028 order intake เข้ามาแล้วทั้งที่ lead time ปกติ 2 ปี *(q2-2026-call.md l.42-44, 122, 194, verified)* Installed Base Management (service, high-margin) โต >30% guidance FY2026 *(l.70, verified)* — แต่ลูกค้า leading-edge มีแค่ 5 รายทั่วโลก (TSM, Samsung, INTC, SK Hynix, MU/Kioxia) เป็น structural concentration ไม่ใช่ risk ชั่วคราว *(fundamentals agent)*
- **Margin trend: ดีขึ้นต่อเนื่อง** — Q2 gross margin 54% *(l.12, verified)*, FY2026 guidance 54-56%, Q3 guidance 55-57% *(l.26, 28, verified)* driven by EUV mix shift ไปทาง tool รุ่น E/F ที่ ASP สูงขึ้นใน 2027 และ pricing power ที่เริ่มเห็นจาก capacity ที่ลูกค้าแย่งกันจอง *(fundamentals agent)* — แต่ R&D €1.3B Q2 สูงกว่า guide จาก "technology and IT transformation costs" *(l.100, verified)*
- **Capital allocation: reinvest + คืนทุนสม่ำเสมอ** — buyback €1.1B ใน Q2 ภายใต้ program ใหม่ 2026-2028, cash €7.6B (UNVERIFIED, web) ไม่ต้องสร้าง fab ใหม่จนถึงปี 2028 (capacity มาจาก footprint optimization ล้วนๆ) *(fundamentals agent)*

---

## Latest Earnings — Q2 FY2026
*Source: earnings agent — q2-2026-call.md, all figures EUR (verified line refs)*

- Net sales **€9.3B** (เหนือ high end ของ guidance), gross margin **54%**, net income €2.9B (31.3% ของยอดขาย), EPS €7.59 *(l.10-16)*
- Net system sales €6.6B: EUV €3.8B (รวม High-NA 1 เครื่อง) / non-EUV €2.8B; logic 51% / memory 49% *(l.18)*
- FY2026 guidance ปรับขึ้นเป็น **net sales €43-45B, gross margin 54-56%**; Q3 guidance €11-12B, 55-57% *(l.24-28)*
- Logic sales growth >25% ทั้งปี (3nm AI accelerator, 2nm เริ่ม ramp); memory sales growth >75% ทั้งปี (DDR/HBM demand + price) — อธิบายเป็น structural litho-intensity shift ไม่ใช่แค่ cyclical spike *(l.30-32, earnings agent)*
- 2027 capacity: Low-NA EUV/immersion +30% (65→~85 units) "nearly fully covered with orders"; 2028 อีก +30% กำลัง "investigating" — ยังไม่ commit *(l.42-44, 122, 194)*
- FCF เพียง €1.3B ใน Q2 ทั้งที่ net income €2.9B — earnings-to-cash conversion gap ในไตรมาสเดียว *(l.46, earnings agent)*
- China sales ~20% ของ FY2026 guidance *(l.48)*

---

## Bull / Bear

**Bull** *(bull_researcher)*
- **Cornered resource + Counter-positioning:** Intel Foundry ใช้ High-NA EUV ผลิตจริงแล้วบน 18A — milestone ที่ไม่มีคู่แข่งไปถึง; R&D bill ของ next-gen litho "only makes sense at ASML's volume" *(valuation agent; q2-2026-call.md l.60, 124)*
- **Scale economies compounding เป็น pricing power:** China ลด (33%→~20%) พร้อมกับ margin guidance ที่ขึ้น (54-56%) — แปลว่าส่วนที่หายไปถูกแทนที่ด้วย demand คุณภาพสูงกว่า (E/F tool mix 2027) ไม่ใช่ demand ที่หดตัว *(fundamentals agent)*
- **Process power ใน memory inflection:** memory growth >75% ถูกอธิบายเป็น structural litho-intensity shift (multi-patterning → single-expose EUV) ไม่ใช่ sugar high ปีเดียว บวกกับ 2027 order coverage เกือบเต็มและ 2028 เริ่มมี order เข้าแล้ว *(earnings agent l.42-44, 122, 194)*

**Bear** *(bear_researcher)*
- **Concentration เป็น single-digit-customer bet:** มีแค่ 5 รายทั่วโลกที่ใช้ leading-edge EUV ได้ *(fundamentals agent)* China เคยถูก guide ลงมาที่ ~25% แต่จริงจบที่ 33% ของ FY2025 (UNVERIFIED, web) — ประวัติ undershoot guidance ของตัวเอง ทำให้ ~20% ของ FY2026 อาจ optimistic ซ้ำแบบเดิม *(sentiment agent, UNVERIFIED)*
- **Backlog มองดูยาวกว่าที่เป็นจริง:** backlog €38.8B (UNVERIFIED, web) เทียบ run rate ใหม่ ~€44B คือ visibility ต่ำกว่า 1 ปี ไม่ใช่ "years of visibility" ตามที่ bull เล่า — valuation agent เองก็บอกว่า 2027 coverage "supports one more strong year; it does not yet support the multi-year extrapolation the multiple implies" ที่ ~49x forward P/E บน 10-year revenue CAGR จริงแค่ 15-18% *(valuation agent)*
- **Bear point ที่ bull ไม่มี counter เลย — competitive encroachment ที่เกิดขึ้นจริงแล้ว:** Canon nanoimprint lithography มี pilot จริงที่ Kioxia แทนที่ EUV layer ได้ 20-30% แล้ว ไม่ใช่แค่ roadmap slide (Nikon ก็ undercut ราคาใน DUV รุ่นเก่า) — ไม่มี analyst คนไหนใน 3 ตัวที่เหลือ (fundamentals/earnings/valuation) พูดถึงจุดนี้เลย ซึ่งเป็น tell ว่า cornered-resource thesis ที่อ้าง "ไม่มีทางเลือกอื่น" ไม่ได้นับ substitute ที่กำลัง run จริงในโรงงานลูกค้า *(sentiment agent, UNVERIFIED)*

---

## Valuation

*Lens: forward P/E vs. growth/PEG, cross-checked กับ unit-order backlog coverage — ไม่ใช่ DCF ตรงๆ เพราะ ASML เป็น capital-equipment monopoly ที่ revenue ส่วนใหญ่ pre-book ผ่าน customer commitment (valuation agent)*

Market cap ที่ราคา $1,743.94 ≈ $686B (~€635B) เทียบ FY2025 net income €9.6B (UNVERIFIED) = trailing P/E ~66x; เทียบ FY2026 guidance (net income โดยประมาณ ~€13B) = forward P/E ~49x บน sales growth ~35% และ earnings growth ~40% ปีนี้ → PEG ~1.2-1.4x ราคานี้ต้องการให้ (1) FY2026 acceleration (memory >75%, logic >25%) repeat ในรูปแบบใดรูปแบบหนึ่งผ่านปี 2027 (2) gross margin ยืนโซน 54-56% ระหว่างที่ High-NA ramp และ (3) ไม่มี customer เสีย share ให้ alternative ใดๆ

2027 order coverage สนับสนุน "อีกหนึ่งปีที่แข็งแรง" แต่ยังไม่สนับสนุน multi-year extrapolation ที่ multiple นี้ implied อยู่ — 10-year revenue CAGR จริงของ ASML อยู่ที่ 15-18% เท่านั้น ไม่ใช่ระดับที่ราคาวันนี้ capitalize อยู่ China mix cut ถูก price-in ใน guidance แล้ว แต่ MATCH Act ยังเป็น unpriced tail risk ที่ยังไม่ผ่านเป็นกฎหมาย

**Verdict: Ahead of itself**

**Falsifying number:** FY2027 net sales growth guidance (ให้พร้อม Q4/FY2026 results, ~ปลาย ม.ค. 2027) **ตั้งแต่ 20% YoY ขึ้นไป** พร้อม memory-segment growth guidance ≥30% — ถ้าเกิด แปลว่า acceleration ต่อเนื่องหลายปีที่ราคาต้องการกำลังเกิดจริง และ verdict "Ahead of itself" ผิด

*Integrator note (2026-09-28):* falsifier ฉบับแรกเขียนกลับทิศ ("ต่ำกว่า 20%") ซึ่งจะ *ยืนยัน* verdict ไม่ใช่หักล้าง — แก้เป็นทิศที่ถูกแล้ว

*Integrator note:* bear ชี้ถูกว่า backlog €38.8B (UNVERIFIED) เทียบ run rate ใหม่คือ visibility ไม่ถึง 1 ปี — "Ahead of itself" ขึ้นกับว่า FY2027 guidance ที่จะออกต้นปี 2027 ยืนยัน multi-year trend หรือเป็นแค่ one-year AI capex spike

---

## Variant Perception

- *Thesis metric:* **FY2027 net sales/memory growth guidance เทียบ FY2026 (>25% logic, >75% memory)** — ถ้าลดลงมากกว่าครึ่ง แปลว่า acceleration ปีนี้ไม่ durable
- *Where we differ from consensus:* nothing — we hold the consensus view (Strong Buy ~91%, PT เฉลี่ย ~$2,135, UNVERIFIED web) สิ่งที่เราเฝ้าเพิ่มจาก debate round คือ **Canon nanoimprint pilot ที่ Kioxia** ซึ่งไม่มี analyst ฝั่ง fundamentals/earnings/valuation พูดถึงเลย — เป็น blind spot ที่ควรติดตาม ไม่ใช่ edge ที่เรามีเหนือตลาด

---

## Kill Conditions

Thesis: *ASML เป็น sole EUV supplier ที่ leading-edge fab ทุกรายต้องพึ่งพา และ AI-driven capex cycle นี้จะยืดยาวหลายปีผ่าน High-NA ramp*

- **MATCH Act ผ่านและขยาย export control จาก EUV ไปครอบคลุม DUV ทั้งหมดสำหรับ 5 fab จีนที่ระบุชื่อ (SMIC, YMTC, CXMT, Hua Hong, Huawei)** — China ปัจจุบัน ~20% ของ FY2026 guidance (ลดจาก 33% FY2025 แล้ว) การตัดเพิ่มเติมซ้อนทับบน base ที่ลดไปแล้ว `[bounded ~15%]`
- **TSM/Samsung/INTC/SK Hynix/MU ชะลอ capex พร้อมกันจาก AI demand ที่พิสูจน์ว่าเป็น one-year spike** — FY2027 order book ที่ "close to fully covered" หายไปทันที เพราะ concentration risk ที่มีลูกค้าแค่ 5 ราย `[bounded ~40%]`
- **Canon nanoimprint หรือ Nikon DUV alternative เข้าถึง sub-3nm/leading-edge production จริง** (ไม่ใช่แค่ pilot ที่ non-critical layer 20-30%) — cornered-resource thesis พังทันที เพราะไม่มีตัวเลข damage ที่ sized ได้ล่วงหน้า `[open-ended]`
- **High-NA EUV adoption ไม่ขยายเกิน Intel ภายในสิ้นปี 2027** — ถ้า TSM, Samsung, หรือ memory maker ไม่ถึง production milestone growth driver หลักของ 2027-2028 capacity plan จะหาย `[bounded ~25%]`

*ปรับปรุง 2026-09-26: เงื่อนไข China เดิม ("ขยายไปครอบคลุม EUV") ถูก supersede เพราะ EUV ถูกแบนไปจีนอยู่แล้วตั้งแต่ก่อนหน้านี้ (sentiment agent) — เปลี่ยนเป็น MATCH Act ขยายไป DUV ซึ่งเป็น bar ที่สูงกว่าเดิม (ต้องผ่านกฎหมายใหม่) ไม่ใช่การผ่อนคลาย เงื่อนไข "competitor ใหม่ประกาศ EUV alternative" ก็ปรับให้เจาะจงขึ้นเป็น "เข้าถึง production จริงที่ leading edge" หลังพบว่า Canon pilot มีอยู่แล้วที่ non-critical layer — เป็นการยกระดับเกณฑ์ให้ตรงกับสถานะปัจจุบัน ไม่ใช่การลดเกณฑ์*

---

## What to Ask

1. **China ~20% ของ FY2026 guidance นี้ conservative พอไหม?** ในเมื่อ FY2025 เคย guide ~25% แต่จบที่ 33% จริง (UNVERIFIED) — pattern undershoot ตัวเองซ้ำได้อีกไหม
2. **FY2027 net sales/memory growth guidance (ต้นปี 2027) จะยืนยัน trend หรือเป็นแค่ one-year AI spike?** นี่คือ falsifying number ของ valuation ตรงๆ ต้องติดตามให้ทัน
3. **Canon nanoimprint pilot ที่ Kioxia ขยายไปเกิน 20-30% ของ layer หรือไปถึง node ที่เล็กลงหรือยัง?** เป็น blind spot ที่ analyst 3 ใน 4 ไม่ได้พูดถึงเลยในรอบนี้

---

*ไม่ใช่คำแนะนำการลงทุน — research summary จาก Q2 FY2026 call, web research (UNVERIFIED ตามที่ระบุ) และ agent analysis*

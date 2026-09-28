---
ticker: AVGO
company: Broadcom
updated: 2026-09-26
type: stock-brief
shared_driver: ai-capex
---

# AVGO — Broadcom Inc.
**Date:** 2026-09-26 | *Refresh of the 2026-06-07 brief via /deep — adds Q3 FY2026 call, debate round, valuation verdict, variant perception, damage-tagged kill conditions. Price $352.81 (yfinance, 2026-09-26)*

**Source docs:** [[sources/AVGO/10-k-fy2025]] · [[sources/AVGO/q3-2026-call]]

---

## Company Snapshot

Broadcom ทำรายได้จากสองธุรกิจ: Semiconductor Solutions (custom AI accelerator/XPU สำหรับ hyperscaler, Ethernet switching, RF filter, storage) และ Infrastructure Software (VMware/VCF หลังเข้าซื้อ VMware $69B ปี 2023) FY2025 semiconductor = 58% ของรายได้, software = 42% *(fundamentals agent, 10-k-fy2025.md l.14-15)* ตอนนี้ AI semiconductor กลายเป็นเครื่องยนต์หลัก — Q3 FY2026 คิดเป็น 56% ของรายได้รวมทั้งบริษัท โตจากปีก่อน 221% *(earnings agent, q3-2026-call.md l.16)* ลูกค้าหลักคือ hyperscaler ที่ทำ custom silicon สำหรับ AI: [[GOOG]] (TPU), Meta, OpenAI, Anthropic — Broadcom เป็นหนึ่งในไม่กี่รายที่ออกแบบ ASIC ระดับนี้ได้ ทำให้จุดตัดกับ [[NVDA]] ในตลาด AI compute ชัดเจนขึ้นทุกไตรมาส

## Fundamentals Signal

- **Revenue durability: สูงขึ้นเรื่อยๆ** — FY2025 total revenue $63.89B (+24% YoY): Semiconductor $36.86B (+22%), Infrastructure Software $27.03B (+26%) *(10-k-fy2025.md l.819-823, verified)* แต่ concentration ก็สูงตาม: distributor รายเดียว = 32% ของรายได้, top-5 end customer = 40% *(10-k-fy2025.md l.795, l.797, verified)*
- **Margin trend: ขยายตัวทั้งสองด้าน** — gross margin 68% (จาก 63%), operating margin 40% (จาก 26%, op income $25.48B +89%) *(10-k-fy2025.md l.776, l.841-843, verified)*; Infrastructure Software segment margin 76.8% (จาก 65.0%) *(fundamentals agent)*
- **Capital allocation: จ่ายหนี้ + ลงทุนต่อ** — debt $67.12B (UNVERIFIED — ไม่พบในไฟล์ 10-K ในเครื่อง) แต่ interest expense ลดจาก $3.95B → $3.21B; R&D $10.98B (+18%); SBC $7.57B (+33%); dividend $11.14B + buyback $2.45B *(10-k-fy2025.md l.938-976, verified)*

## Latest Earnings — Q3 FY2026 (reported ~Sept 2026)

- **Revenue $29.6B (+86% YoY)**; non-GAAP operating income $20.1B (+92%); non-GAAP EPS $3.32 (+96%) *(q3-2026-call.md l.10-14, verified)*
- **AI semiconductor revenue $16.7B (+221% YoY, +54% QoQ) = 56% ของรายได้รวม** *(l.16, verified)* — FY2026 AI guidance ปรับขึ้นเป็น **$58B (+186%)**; FY2027 outlook **$115B**, FY2028 **$230B**, บริษัทบอกว่า "secured supply" ไม่ใช่แค่ pipeline *(l.18-20, verified)*
- **Non-AI semiconductor แบนสนิท** — $4.2B (+5% YoY, flat QoQ) *(l.32, verified)* — การเติบโตทั้งหมดตอนนี้พึ่ง AI segment
- **Gross margin ลดจาก AI mix** — 75% ใน Q3 (ลด 210bps QoQ), Q4 guide ~73% — แต่ operating margin ยังขึ้น (67.9%, +240bps YoY) เพราะ opex leverage ชดเชยได้ *(l.38-40, l.148, verified)*
- **Infrastructure Software $8.8B (+29% YoY), VMware ARR +15%** *(l.24, verified)*; **FCF $13.7B = 46% ของรายได้** ใช้จ่ายหนี้ $5.6B ใน Q3 + $1.5B หลังปิดไตรมาส *(l.26, l.44, verified)*
- **Customer roadmap ที่ระบุชื่อ**: Google TPU (สัญญาระยะยาว "multi-tens of billions" ต่อปี), Anthropic (5GW ปี 2027, 10GW ปี 2028 — จะเป็นลูกค้า XPU รายใหญ่สุดในปี 2027), OpenAI (1.3GW ปี 2027, 5GW+ ปี 2028), Meta (3GW ตลอด 3 generation ถึงปี 2027-28) *(l.126-136)*
- **XPV third-party financing $35B tranche แรก** ปิดเดือนมิ.ย. สำหรับ deployment 1GW ของ Anthropic — เป็นเงินทุนนอกงบดุล Broadcom เอง *(l.42, l.156)*
- ผู้บริหารบอกว่า "on target to exceed $30 in earnings per share in fiscal 2028" *(l.142, verified, paraphrased)*

## Bull / Bear

**Bull** *(bull_researcher)*
- **Cornered resource ไม่ใช่ concentration risk** — top-5 = 40%, distributor เดียว = 32% *(fundamentals, l.797/795)* แต่มองกลับกัน: ลูกค้าเหล่านี้ล็อค capacity หลายปีล่วงหน้าระดับ gigawatt (Anthropic, OpenAI, Meta, Google) — demand เกิน supply ไม่ใช่ Broadcom พึ่งลูกค้าไม่กี่ราย แต่ลูกค้าต้องพึ่ง design capacity ที่หายากของ Broadcom *(earnings, l.20)*
- **Switching cost ทบต้นทุก chip generation** — co-design กับ TPU v8i, Jalapeno, Meta chip ฝัง Broadcom เข้า roadmap ของ hyperscaler ไปหลายปี FY2027/FY2028 outlook อิงจาก "secured supply" ไม่ใช่ pipeline หวังผล
- **Operating margin ยังขยายแม้ gross margin ลด** — 67.9% (+240bps YoY) จาก operating leverage แม้ AI mix ดึง gross margin ลง 210bps — Infrastructure Software เป็นฐานกำไรสำรองที่ margin 76.8% และ ARR โต 15%
- **หนี้กำลังลดจากกระแสเงินสด AI เอง** — FCF 46% ของรายได้จ่ายหนี้ $5.6B+$1.5B ใน Q3 เดียว; XPV financing ย้าย capex intensity ออกจากงบดุล Broadcom
- **Valuation ที่ 11.8x เป้า EPS ผู้บริหารเองปี 2028** *(valuation agent)* — ต่ำกว่า multiple ทั่วไปสำหรับธุรกิจที่ guide โตต่อเนื่องเกือบเท่าตัวทุกปีถึงปี 2028

**Bear** *(bear_researcher)*
- **Concentration คือเรื่องทั้งหมด ไม่ใช่ diversification** — AI growth narrative พึ่งลูกค้าที่ระบุชื่อได้ราว 6 ราย (Google, Meta, OpenAI, Anthropic + อีก 2) ไม่ใช่ hyperscaler wave กว้างๆ สัญญาพวกนี้ renegotiate/delay/insource ได้ทุกเมื่อ
- **Gross margin กำลังกร่อนจริง ไม่ใช่แค่ทฤษฎี** — ลด 210bps QoQ เพราะ AI mix, Q4 guide ต่ำกว่าอีก (~73%) operating margin ที่ยังขึ้นเป็นเรื่อง cost control ไม่ใช่ pricing power — ถ้าลูกค้า AI ได้ leverage ต่อรองมากขึ้นตามปริมาณ ส่วนกันชนนี้จะหายก่อน
- **หนี้ไม่ได้หายไป แค่ย้ายออกนอกงบดุล** — debt ~$67B (UNVERIFIED) ยังอยู่ในงบ Broadcom แม้จ่ายคืน $5.6B+$1.5B ปีนี้ ขณะที่ XPV $35B financing เป็น contingent liability ที่ valuation agent เองก็ชี้ว่าไม่อยู่ในงบ Broadcom — credit risk ของ AI buildout ถูกเก็บไว้ที่อื่น ถ้า counterparty สะดุด (เช่น lab ที่ยังขาดทุน) ความเสี่ยงย้อนกลับมาได้
- **Non-AI semiconductor แบนสนิท** — $4.2B, +5% YoY เท่านั้น, flat QoQ — ธุรกิจ semiconductor เดิมไม่โตเลย ทั้ง thesis พึ่ง AI customer กลุ่มเดิมกลุ่มเดียว
- **Bear point ที่ไม่มี bull counter**: อัตราการโตกำลังชะลอตัวตามตัวเลขที่บริษัทเองให้ — +221% (Q3 จริง) → +186% (FY26 guide) → ~100% (FY27/28 outlook) นี่คือ fact จากบริษัทเอง ไม่ใช่ bear คาดเดา รวมกับ concentration แล้ว คือฐานที่แคบลงและอัตราโตที่ช้าลง ไม่ใช่ demand ที่ขยายวงกว้างอย่างที่ bull เล่า

## Valuation

*Lens: sum-of-parts / expectations-investing ยึดเป้า EPS ของผู้บริหารเองมากกว่า blended multiple เพราะ AI mix ทำ gross margin ลงพร้อม operating margin ขึ้นพร้อมกัน — multiple เดียวจะบิดเบือน (valuation agent)*

ที่ราคา $352.81 เท่ากับ ~11.8x เป้า EPS ผู้บริหาร "$30+ ภายใน FY2028" *(q3-2026-call.md l.142, verified)* ต้องการให้ AI segment revenue โตราว 4 เท่าจากฐานรายได้รวม FY2025 ภายในปี 2028 พร้อม operating margin ทรงตัวแถบ 66-68% ที่ทำได้อยู่แล้ว อัตราโตเป็น % กำลังชะลอ (+221% → +186% → ~100%) แต่นั่นคือ continuation ของสัญญาที่ secured แล้ว (Google, Anthropic, OpenAI, Meta) ไม่ใช่การเร่งใหม่ที่ต้องพิสูจน์

**Verdict: Still underrated**

**Falsifying number:** AI semiconductor revenue รายงานในผลประกอบการ Q4 FY2027 (ประมาณ ธ.ค. 2027) ต่ำกว่า $100B (ต่ำกว่าเป้าที่ guide ไว้ $115B เกิน 13%)

*Integrator note:* bull และ bear เห็นตรงกันว่า debt on-balance-sheet กำลังลดจริง — จุดที่ยังเถียงกันไม่จบคือ XPV off-balance-sheet financing เป็นความเสี่ยงจริงหรือเป็นแค่การจัดโครงสร้างทุนที่ฉลาด ยังไม่มีข้อมูลพอจะฟันธง

## Variant Perception

- *Thesis metric:* **AI semiconductor revenue growth rate (YoY %) เทียบกับ guided trajectory** — เพราะ dollar amount โตต่อเนื่องอยู่แล้ว แต่สิ่งที่ตลาดจะตัดสินคือ % ชะลอเร็วกว่าที่ guide หรือไม่ ($58B → $115B → $230B)
- *Where we differ from consensus:* nothing — we hold the consensus view (Strong Buy, PT เฉลี่ย ~$531.85, web UNVERIFIED) สิ่งที่เราเฝ้าเพิ่มคือ **สัดส่วนรายได้ XPU ที่มาจาก XPV-financed deployment** ซึ่งบริษัทไม่แยกเปิดเผยชัดเจนว่าส่วนไหน "ขาย" จริงกับส่วนไหน "financed" ผ่าน vehicle ของตัวเอง — ถ้าสองอย่างนี้ปนกันอยู่มาก revenue quality จะต่ำกว่าที่ตัวเลขบอก

## Kill Conditions

Thesis: *AI semiconductor design relationship กับ hyperscaler รายใหญ่จะ compound เป็น switching cost + operating leverage ที่พิสูจน์ตัวเองต่อเนื่องถึง FY2028*

1. **ลูกค้า AI XPU รายใหญ่ (Google, Meta, OpenAI, หรือ Anthropic) ถอนหรือเลื่อน gigawatt deployment ที่ผูกไว้** — AI semiconductor เป็น 56% ของรายได้รวมและกระจุกที่ลูกค้าราว 6 ราย *(bear point ไม่มี bull counter บน concentration)* `[bounded ~50%]`
2. **AI semiconductor revenue โตต่ำกว่า guided trajectory สองไตรมาสติด** — FY2027 ต่ำกว่า $100B เทียบ guide $115B (= falsifying number) `[bounded ~40%]`
3. **Gross margin ที่ลดจาก AI mix เริ่มลาก operating margin ลงจริง** แทนที่ opex leverage จะชดเชยได้เหมือนที่ผ่านมา — สัญญาณว่าลูกค้าเริ่มมี pricing power เหนือ Broadcom `[bounded ~30%]`
4. **XPV หรือ third-party financing vehicle มีปัญหา counterparty** (เช่น AI lab ที่ยังขาดทุนไม่สามารถชำระตามสัญญา financed capacity) ทำให้ contingent liability ย้อนกลับมาที่ Broadcom `[bounded ~20%]`
5. **Hyperscaler ทีม in-house ASIC เข้ามาแทนที่ Broadcom เป็น design partner ใน chip generation ถัดไป** — ไม่มีเพดานความเสียหายที่มองเห็น เพราะเป็นการเสีย relationship เชิงโครงสร้าง ไม่ใช่แค่ยอดขายไตรมาสเดียว `[open-ended]`

*Loosened 2026-09-26: เอา kill condition เดิม "VMware churn เพิ่ม QoQ" (brief 2026-06) ออก — Q3 FY2026 call แสดง VMware ARR +15% YoY ต่อเนื่อง ไม่มีสัญญาณ churn (earnings agent l.24) หลักฐานไม่รองรับให้เป็น thesis-breaking แล้ว ย้ายไปเป็นคำถามเฝ้าดูใน "What to Ask" แทน และ kill condition เดิม "debt ไม่ deleverage ตามคาด" ถูกแคบลงเหลือเฉพาะความเสี่ยง XPV off-balance-sheet เพราะหนี้บนงบดุลกำลังลดเร็วกว่าคาด ($5.6B+$1.5B จ่ายคืนใน Q3 เดียว, interest expense ลดจาก 10-K) — การ loosen ครั้งนี้สะท้อนความคืบหน้าจริงเรื่อง deleverage ไม่ใช่การรีบแก้ก่อนโดน trigger.*

## What to Ask

1. **XPU revenue ที่มาจาก XPV-financed deployment คิดเป็นสัดส่วนเท่าไหร่ของ AI semiconductor revenue?** — ถ้าสัดส่วนสูง revenue quality ควรถูกหักส่วนลด ไม่ใช่นับเต็มเหมือน sale ปกติ
2. **VMware ARR +15% นี้ยั่งยืนแค่ไหนหลัง renewal cycle รอบใหญ่ผ่านไป?** — ยกเลิกจากการเป็น kill condition แล้ว แต่ยังควรติดตามทุกไตรมาสว่า churn เริ่มขึ้นหรือไม่ โดยเฉพาะเทียบกับ Nutanix/OpenShift ที่เคยเป็น alternative หลัง VMware ปรับราคา
3. **Non-AI semiconductor ที่แบนที่ $4.2B จะกลับมาโตไหม หรือจะถูกลดความสำคัญลงเรื่อยๆ** — ถ้าทั้งบริษัทกลายเป็น "AI pure-play" โดยพฤตินัย risk profile เปลี่ยนจากที่เคยกระจายความเสี่ยงด้วยสอง engine
4. **AVGO vs [[NVDA]] ใน AI compute spending** — hyperscaler แบ่งงบ custom XPU vs GPU อย่างไรใน 2027-2028 และ margin ของแต่ละฝั่งต่างกันแค่ไหนเมื่อ mix เปลี่ยน
5. **[[MU]] และ supply chain memory ที่ทำให้ gross margin ของ XPU ต่ำกว่า** — ถ้าต้นทุน memory ยังแพงต่อเนื่อง gross margin 73%→ต่ำกว่านี้อีกหรือไม่ในปี 2027

---

*ไม่ใช่คำแนะนำการลงทุน — research summary จาก 10-K FY2025, Q3 FY2026 call และ agent analysis*

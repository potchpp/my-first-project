---
ticker: ORCL
company: Oracle
updated: 2026-09-25
type: stock-brief
shared_driver: ai-capex
---

# ORCL — Oracle Corporation
**Date:** 2026-09-25 | *Refresh of the 2026-09-18 brief — adds Q1 FY2027 call, credit/FCF status, valuation, variant perception, damage-tagged kill conditions. **Kill condition #4 has fired — see status note.***

**Source docs:** [[sources/ORCL/10-k-fy2026]] · [[sources/ORCL/q1-2027-call]]

---

## Company Snapshot

Oracle ขาย enterprise software (database, apps, support) ที่ mature และกำไรสูง และกำลังใช้เงินกู้ + เงินเพิ่มทุนสร้าง **OCI (Oracle Cloud Infrastructure)** เป็น AI cloud ขนาดใหญ่ — cloud infrastructure โต **+121%** และ backlog (RPO) **$664B** แต่ ~45% ของ backlog ผูกกับ **OpenAI** รายเดียว *(third-party estimate)* และ **FCF ติดลบต่อเนื่อง** ขณะที่ credit rating อยู่ห่าง junk แค่ขั้นเดียว *(earnings + sentiment agents)*

## Fundamentals Signal
*Source: sources/ORCL/10-k-fy2026.md (prior brief, fundamentals agent)*

**Revenue durability — โตเร็ว, backlog ใหญ่, แต่กระจุก:** FY26 revenue $67.4B (+17%); cloud+software 87% ของรายได้ (+19%); OCI = 53% ของ cloud revenue (จาก 35% สองปีก่อน) ขับ 84% ของ cloud growth; สัญญา 1–5 ปี

**Margin trend — ถูกกดจาก buildout:** cloud/software margin % ลดลงเพราะ infra cost (opex +$7.0B, ในนั้น $6.0B เป็น infra) *(10-K)*; Q1 FY27 gross margin ลด "ตามคาด" แต่ non-GAAP op margin ทรงตัว 42% เพราะตัด opex *(q1-2027-call)*

**Investment or decay? — Investment แต่ด้วยเงินคนอื่น:** revenue เร่ง (+17% → +30%), capex พุ่ง, margin ขั้นต้นลด = สร้าง S-curve ใหม่จริง — แต่ fund ด้วยหนี้และการเพิ่มทุน ไม่ใช่ cash ของตัวเอง

**Capital allocation — capex treadmill + dilution**
- FY26: capex $55.7B, fund ด้วย senior notes $42.7B + mandatory convertible preferred $5.0B; buyback $95M, ปันผล $5.8B *(10-K)*
- Q1 FY27: **ขายหุ้นเพิ่มทุน $20B ผ่าน at-the-market (dilutive)** *(q1-2027-call, verified)*; FY27 capex $90–95B gross, ≤$70B net of customer prepayments
- Net debt ~$88B + preferred $5B (+ lease $30.6B) *(valuation agent, Q1 FY27 10-Q)*; debt-to-equity ~427% vs [[MSFT]] ~33%

## Latest Earnings — Q1 FY2027 (quarter ended Aug 2026)
*Source: sources/ORCL/q1-2027-call.md (earnings agent; key lines verified by PM)*
- Revenue **$19.3B (+30%)**; cloud infrastructure **$7.4B (+121%, เร่งจาก +93%)**; cloud apps $4.2B (+10%); non-GAAP EPS $1.92 (+30%); non-GAAP op margin 42% (flat)
- **RPO $664B** (+$209B YoY), ส่วนใหญ่ prepay หรือลูกค้านำ hardware มาเอง; $30B AI bookings ใน Q1 ไม่ต้องใช้ capex เพิ่ม; ~50% แปลงเป็นรายได้ใน 36 เดือน
- GPU utilization 97.9%; renewal ราคาสูงขึ้น 20% แม้ hardware อายุ 4 ปี
- OCF $23B (record) แต่ capex $28B gross / $18B net → **FCF −$5B**; **ไม่ให้ timeline ว่า FCF จะกลับเป็นบวกเมื่อไหร่** *(verified)*
- **FY27 guide ขึ้น:** revenue ≥$90B (+34%), EPS $8.10; Q2 revenue +30–34%, cloud +65–71%
- OpenAI: ความสัมพันธ์ขยาย (GPT-6 train ที่ Abilene); ไม่มีการพูดถึง renegotiation
- **Direction vs last quarter:** ขึ้นในแง่ revenue/backlog; แย่ลงในแง่ cash และ balance sheet
- *PM correction: earnings agent บอกว่า Q1 FY27 เป็น "ไตรมาสแรกที่ FCF ติดลบ" — ผิด (Q1 FY26 −$5.4B; FY26 ทั้งปี ~−$23.7B ตาม web, unverified)*

## Why the Stock Fell ~57%
*Source: sentiment agent (web)*
- Peak $322.54 (ต.ค. 2025) → $139.54; −3.5% วันนี้
- **S&P ลด rating เป็น BBB- (18 ก.ย. 2026)** ห่าง junk หนึ่งขั้น; Moody's outlook ลบ; CDS ~203bp สูงสุดในรอบ 18 ปี; หุ้นกู้ 10 ปี yield ~6.5% *(sentiment agent)*
- ความกังวล OpenAI: commitment ~$300B/5 ปี เทียบรายได้ OpenAI ~$2B/เดือน — ต้องพึ่ง funding round ($122B) และ IPO ต้นปี 2027
- *Unverified (แหล่งคุณภาพต่ำ):* force majeure ที่ Project Jupiter (NM, 4.5GW) และ layoff — สาเหตุที่อ้างของ −3.5% วันนี้

## Bull / Bear

**Bull:**
- **Scale economies ใน OCI กำลังเร่ง ไม่ใช่หมดแรง:** cloud infra +93% → +121%, GPU ใช้งาน 97.9%, renewal ราคา +20% บน hardware เก่า — capacity ที่มีคนแย่งกันใช้ *(bull_researcher; earnings agent)*
- **Backlog ที่ลูกค้ารับความเสี่ยงบางส่วนเอง:** RPO $664B ส่วนใหญ่ prepay/ลูกค้านำ hardware มา; $30B bookings ใน Q1 ไม่ต้องลงทุนเพิ่ม; ลูกค้ามี [[META]], [[NVDA]], [[AMD]], xAI, TikTok นอกจาก OpenAI *(bull_researcher; earnings + sentiment agents)*
- **ราคาสะท้อนความเสี่ยงแล้ว:** ~12.7x EPS FY28; แม้ OpenAI ส่วนนั้นไม่แปลงเลย SOTP ยังให้ ~$110/หุ้น *(bull_researcher; valuation agent)* — *PM note: EPS เป็น non-GAAP ไม่รวม SBC และค่าเสื่อมที่กำลังพุ่ง P/E จริงสูงกว่านี้*

**Bear:**
- **เผาเงินไม่มีวันสิ้นสุดที่ประกาศ:** FCF ติดลบหลายไตรมาสติด, FY27 capex $90–95B, ไม่มี timeline FCF บวก — และ fund ด้วยการเพิ่มทุน $20B + หุ้นกู้ ไม่ใช่แผนลดหนี้ *(bear_researcher; earnings agent + PM findings)*
- **Credit ที่ขอบ junk:** BBB-, Moody's ลบ, CDS สูงสุด 18 ปี — ทั้ง capex plan ขึ้นกับการเข้าถึงตลาดทุน *(bear_researcher; sentiment agent)*
- **RPO ไม่ใช่เงินสด และกระจุก:** ~45% ของ backlog คือ OpenAI ซึ่งเองก็ยังขาดทุนและพึ่ง IPO; margin ขั้นต้นกำลังลด — op margin ทรงได้เพราะตัด opex *(bear_researcher; sentiment + earnings agents)* — *PM note: bear ประเมิน OpenAI shrink ที่ ~40–45% ของมูลค่า — สูงเกิน SOTP ให้ ~20–25%*

## Valuation
*Source: valuation agent (price $139.54 Yahoo 2026-09-25, 3.024B shares, market cap ~$422B, net debt ~$88B + $5B preferred → EV ~$515B, excl. $30.6B leases)*

- **Lens: sum-of-parts บน EV** — P/E หลอกเพราะ non-GAAP ไม่รวม SBC/ค่าเสื่อม, FCF ติดลบ, และ capex ถูก fund บางส่วนด้วย prepayment ลูกค้า
- (a) Mature software (apps + support + license + hardware/services ~$49B revenue, margin ~45% *(ประมาณ)*) × 18x ≈ **$330B**
- (b) **OCI residual ≈ $185B** + capex สุทธิที่ยังต้องลงอีก ~$100B → จาก RPO ~$130B/ปี ที่ run-rate ต้องการ **OCI op margin ~26–30%** — ใกล้กับ incremental margin ที่ OCI แสดงอยู่ (~33%, inference)
- ถ้า OpenAI (~45% ของ RPO) ไม่แปลงเลย → ~$110/หุ้น
- **Implied expectation:** continuation — OCI แปลง backlog ที่ margin ปัจจุบัน ไม่ต้องเร่ง; ความเสี่ยงอยู่ที่ execution + funding
- **Verdict: Deserved**
- Consensus EPS FY27 $8.14, FY28 $11.00 (~12.7x FY28) *(Yahoo)*; 52-week $114.50–$322.54
- **Falsifying number:** non-GAAP op margin **<40%** ใน Q3 FY27 (~กลาง มี.ค. 2027) → buildout ส่งมอบที่ margin ต่ำกว่าที่ราคาต้องการ → Ahead of itself

## Variant Perception
- *Thesis metric:* **FCF หลัง capex + net capex** (ตัววัดว่า buildout จ่ายตัวเองได้) คู่กับ **RPO conversion** และ non-GAAP op margin
- *Where we differ from consensus:* **ไม่มี — เราถือ consensus view** ราคาสะท้อนทั้ง backlog และความเสี่ยงทางการเงินแล้ว

## Kill Conditions
1. **OpenAI ผิดนัดชำระหรือ renegotiate สัญญาลงอย่างมีนัยสำคัญ** `[bounded ~20–25%]` — *Status 2026-09-25: ยังไม่ fire — ความสัมพันธ์ขยาย (GPT-6 ที่ Abilene); ขึ้นกับ OpenAI IPO ต้นปี 2027*
2. **Credit rating ถูก downgrade เข้า junk** `[open-ended]` — capex $90–95B ต้องพึ่งตลาดทุน; ถ้า junk ต้นทุนเงินพุ่งและอาจต้องเพิ่มทุนต่อที่ราคาต่ำ ไม่มี floor ที่มองเห็น — *Status: ใกล้ — BBB- (ห่างหนึ่งขั้น), Moody's outlook ลบ*
3. **Cloud/software margin ลดลงต่อเนื่อง 2+ ไตรมาสติด** โดยไม่เห็นสัญญาณว่า infra cost จะ stabilize `[bounded ~30%]` — *Status: gross margin ลด, op margin ทรง 42% ด้วยการตัด opex — เฝ้าดู*
4. **Free cash flow ติดลบต่อเนื่องเกิน 3–4 ไตรมาส โดยไม่มี debt reduction plan ชัดเจน** `[open-ended]`
   ***Status 2026-09-25: FIRED (very likely)*** — FCF ติดลบตั้งแต่อย่างน้อย Q1 FY26 (−$5.4B) ถึง Q1 FY27 (−$5B), FY26 ทั้งปี ~−$23.7B *(web, unverified)*; management ไม่ให้ timeline FCF บวก และ fund ด้วยการเพิ่มทุน $20B + หนี้ — ไม่ใช่แผนลดหนี้
   *เงื่อนไขนี้ถูกเขียนไว้ตอนที่รู้อยู่แล้วว่าจะมี buildout — มันจึง fire ตามที่ออกแบบไว้ การแก้ถ้อยคำเงื่อนไขนี้ตอนนี้ (หลังมัน fire) คือ ego pattern การตัดสินใจเป็นของผู้ลงทุน: (a) ยอมรับว่า thesis เปลี่ยน หรือ (b) loosen พร้อมเขียนเหตุผลและหลักฐานใหม่ที่ไม่มีตอนเขียนเงื่อนไข*

*Kill conditions 1 และ 3 ต่ำกว่าเกณฑ์ ≥50% — ตามกฎควรย้ายไป Bear แต่การย้าย = loosening ต้องให้ผู้ลงทุนเขียนเหตุผลเอง*

## What to Ask
1. **ถ้า OpenAI ประสบปัญหา Oracle มี contractual protection อะไร?** (prepayment, minimum commitment, capacity ที่ขายต่อได้) — และ OpenAI IPO ต้นปี 2027 เลื่อนได้ไหม?
2. **FCF จะบวกเมื่อไหร่?** management บอกว่าแต่ละโปรเจกต์ให้เงินสดดีหลัง ramp แต่ไม่ให้วันที่ — ถ้าต้องเพิ่มทุนอีกในปี 2027 เจ้าของหุ้นเดิมถูก dilute เท่าไหร่?
3. **ถือ ORCL = เพิ่ม ai-capex exposure เดียวกับ [[NVDA]], [[AMD]], [[TSM]] ฯลฯ** — driver นี้ใกล้ cap 10% แล้ว; ORCL เป็นตัวที่มี balance sheet เสี่ยงที่สุดในกลุ่ม

---
ticker: GMAB
company: Genmab A/S
updated: 2026-09-26
type: stock-brief
shared_driver: pharma-pipeline
---

# GMAB — Genmab A/S
**Date:** 2026-09-26 | *Refresh of the 2026-09-18 brief via /deep — adds H1 2026 call, debate round, valuation verdict, variant perception, damage-tagged kill conditions. Price $35.32 (Yahoo, 2026-09-26)*

**Source docs:** [[sources/GMAB/q2-2026-call]]

> ⚠️ **Data limitation:** Genmab เป็น Danish company ที่ file Form 20-F (ไม่ใช่ 10-K) — fetch script ดึงได้แค่ 10-K เท่านั้น จึงไม่มี local filing ให้ agent ทั้ง 4 อ้างอิง มีแค่ H1 2026 earnings call transcript (`sources/GMAB/q2-2026-call.md`) เป็น local source เดียว ตัวเลข company-specific อื่นๆ ทั้งหมดมาจาก web และถูก label **UNVERIFIED (web)**

---

## Company Snapshot

Genmab เป็น Danish biotech ที่ co-invent **daratumumab (Darzalex)** ซึ่ง J&J เป็นผู้ทำตลาดและเก็บยอดขาย — Genmab ได้แค่ royalty ต่อเนื่อง ไม่ต้องหาลูกค้าใหม่ซ้ำๆ พร้อมมี wholly-owned/self-commercialized pipeline (**Epkinly**/epcoritamab, **Tivdak**) ที่กำลังโตเร็วกว่า royalty base และล่าสุดเพิ่ม **petosemtamab** และ **Rina-S** เข้ามาผ่านการซื้อ Merus (~$8B, ปิดดีล ธ.ค. 2025, UNVERIFIED web) *(fundamentals agent; earnings agent, call l.14, 48; sentiment agent, UNVERIFIED)*

จุดที่ต้องจับตาที่สุด: **Darzalex US patent cliff ปี 2029** (EU 2031, Japan 2030 — ทั้งหมด UNVERIFIED web) — call transcript ของฝ่ายบริหารไม่พูดถึงเรื่องนี้เลยแม้แต่คำเดียว

---

## Fundamentals Signal
*Source: fundamentals agent, citing q2-2026-call.md; supplemented UNVERIFIED (web) where noted*

- **Revenue durability — แยกเป็นสองชั้น:** Darzalex royalty income (ของจริงที่ Genmab ได้) โต **21% YoY** ตามที่ transcript ระบุตรงๆ (call l.48) — เป็น "core driver of total revenue base" **ต้องระวัง:** ตัวเลข $4,207M ที่ transcript ระบุเป็น "DARZALEX Net Trade Sales" (call l.14) คือยอดขายทั่วโลกของ J&J ไม่ใช่รายได้ของ Genmab — earnings agent เคย conflate สองตัวนี้ ผมแก้แล้วในฉบับนี้ Epkinly (H1 2026 $312M, +48% YoY) และ Tivdak (H1 2026 $84M) เป็นรายได้ตัวเองที่ต้องหา site/customer ใหม่ต่อเนื่อง แต่ community adoption สูง — >90% ของ key customer สั่งซื้อ 2+ sites (call l.16, 18, 42, 126)
- **Diversification เกิดขึ้นจริงบางส่วน:** 50% ของ YoY growth มาจาก Epkinly + rest of portfolio, อีก 50% ยังมาจาก Darzalex (call l.28, 138) — ดีขึ้นจาก single-asset dependency แต่ยังไม่ถึงครึ่งทาง
- **Margin trend — ผสม:** Operating profit +18% H1 2026 ช้ากว่า revenue +25% (call l.20, 138, 142) คือ margin compression ระดับ blended แต่ OpEx guidance ขึ้นแค่ 2% ทั้งที่เปิด Phase III petosemtamab ใหม่ 2 โปรแกรม (call l.22, 68) — reinvestment ที่ควบคุมได้ **ข้อควรระวัง:** effective tax rate 3.6% H1 2026 เป็น tailwind ชั่วคราวจาก Merus deferred tax asset ที่ฝ่ายบริหารบอกเองว่าจะ "normalize" ใน 12-18 เดือน (call l.24, 60) — กำไรที่รายงานตอนนี้ปนอยู่กับผลของภาษีที่จะหายไป
- **Capital allocation — reinvest เต็มที่ ไม่มี dividend:** เงินทั้งหมดไปที่ pipeline (petosemtamab, Rina-S, Epkinly frontline) และ Merus integration ไม่มี buyback/dividend เป็น cushion ถ้า readout พลาด *(fundamentals agent)*

---

## Latest Earnings — H1 2026
*Source: earnings agent, citing q2-2026-call.md — call ชื่อ "First Half 26 Financial Results Conference Call" (l.100) ยืนยันว่า Genmab report แบบ H1/FY เท่านั้น ไม่ใช่รายไตรมาสแบบบริษัทอเมริกัน (frontmatter ของไฟล์ label "Q2 FY2026" ทำให้เข้าใจผิดได้ว่าเป็น quarterly cadence)*

- Revenue +25% YoY H1 2026 (l.138); **FY2026 guidance ปรับขึ้นเป็น $4.3-4.5B** (จาก 14% เป็น 19% growth) (l.10); operating profit guidance $1.1-1.4B, +7% vs guidance เดิม (l.12)
- **Darzalex royalty (Genmab's take) +21% YoY** (l.48) — เลขนี้คือ royalty income ไม่ใช่ J&J's $4.207B net trade sales ใน Q2 (l.14) ซึ่งเป็นยอดขายทั่วโลกของสินค้า ไม่ใช่รายได้ Genmab
- Epkinly H1 $312M (+48% YoY, l.16); Tivdak H1 $84M (l.18); proprietary portfolio H1 $396M (+37% YoY, l.26); non-core ex-Darzalex/Epkinly +35% YoY (l.50)
- Pipeline readouts กระจุกตัวที่ **Q4 2026**: petosemtamab head/neck frontline interim (l.30), Rina-S PROC Phase II & III (l.34), Epkinly frontline DLBCL (EPCORE DLBCL-2 interim, l.36); EPCORE DLBCL-4 จบแล้วด้วย PFS benefit ที่ statistically significant ใน chemo-free regimen (l.38) Q1 2027: petosemtamab 2L/3L head/neck OS readout (l.32)
- Transcript **ไม่มีคำว่า** patent cliff, biosimilar หรือ Faspro เลยแม้แต่ครั้งเดียว

---

## Bull / Bear

**Bull** *(bull_researcher)*

- **Process power + cornered resource บน Darzalex royalty:** royalty ที่ Genmab ได้เอง (ไม่ใช่ J&J's gross sales) โต 21% YoY โดยไม่ต้องใช้ commercial spend เพิ่ม — valuation agent ประเมิน NPV ของ annuity ตัวนี้เพียงอย่างเดียวอยู่ที่ $15-20B ทั้งที่ market cap รวมแค่ ~$20.86B *(fundamentals/earnings agent l.48; valuation agent)*
- **Switching costs กำลังก่อตัวใน Epkinly:** >90% key customer สั่ง 2+ sites คือ site-level treatment protocol lock-in ข้าม 2 indication บวกกับ EPCORE DLBCL-4 ที่จบด้วย PFS benefit ชัดเจนในสูตร chemo-free *(fundamentals agent l.16, 42, 126; earnings agent l.38)*
- **Counter-positioning บน capital allocation:** margin compression (op profit +18% vs revenue +25%) เป็นการ reinvest ที่ตั้งใจ — OpEx ขึ้นแค่ 2% ทั้งที่เปิด Phase III ใหม่ 2 ตัว และ diversification math (50% growth มาจาก non-Darzalex แล้ว) แปลว่า "one-trick royalty company" thesis ผิดไปครึ่งหนึ่งแล้วในตัวเลขปัจจุบัน *(fundamentals agent l.20, 28, 68, 138)*

**Bear** *(bear_researcher)*

- **Concentration ที่ relabel เป็น diversification:** Darzalex royalty ยังเป็น "core driver of total revenue base" (l.48) และฐานของมัน — J&J's $4.207B net trade sales — อยู่นอกการควบคุมของ Genmab ทั้งหมด เป็น counterparty dependence ซ้อนบน biotech binary risk ปกติ *(fundamentals/earnings agent l.14, 28, 48, 138)*
- **Margin "growth" ปนอยู่กับ tax artifact:** effective tax rate 3.6% เป็น one-off จาก Merus deferred tax ที่ฝ่ายบริหารเองบอกว่าจะ normalize ใน 12-18 เดือน — หักผลนี้ออก กำไรที่โตจริงจะอ่อนกว่าตัวเลขหัวข่าว *(fundamentals agent l.24, 60)*
- **Balance sheet risk ที่ call ไม่พูดถึง:** ดีล Merus ~$8B ใช้หนี้ใหม่ $5.5B (UNVERIFIED web) มาพร้อมกับช่วงที่ readout ใหญ่ 3 ตัว (petosemtamab, Rina-S, Epkinly frontline) กระจุกอยู่ใน Q4 2026 เดียวกัน — เพิ่ม leverage ก่อนช่วง event risk สูงสุด โดยไม่มี dividend/buyback เป็น cushion *(sentiment agent UNVERIFIED; earnings agent l.30, 34, 36; fundamentals agent)*
- **ไม่มี bull counter:** patent cliff/Faspro risk ที่ management ไม่เคยพูดถึงบน call เลย — sentiment agent (UNVERIFIED web) ให้ estimate ว่า Faspro รักษาได้แค่ 70-80% ของ legacy volume ในกรณีดีที่สุด แปลว่าอย่างน้อย 20-30% ของ royalty base ไม่มีการป้องกันเมื่อถึงปี 2029 และไม่มี analyst agent คนไหนโต้แย้งความเสี่ยงนี้ได้ตรงๆ มีแค่ estimate ที่ยังไม่ verified

---

## Valuation

*Lens: sum-of-parts — royalty-stream NPV (Darzalex/Kesimpta, discount สำหรับ 2029/2031 cliff) + growth multiple บน owned pipeline (Epkinly, Tivdak) (valuation agent)*

ราคา $35.32 ≈ market cap ~$20.86B (UNVERIFIED web) Back-of-envelope royalty annuity NPV (โต ~20% ต่ออีก 3 ปีจนถึง cliff ปี 2029 แล้ว step-down ด้วย Faspro retention 70-80%, discount ~9-10%) อยู่ที่ราว $15-20B เพียงลำพัง เหลือแค่ ~$1-5B ให้ Epkinly/Tivdak ทั้งที่โต 40-48% YoY — ต่ำกว่า multiple ปกติของ oncology biotech ที่โตระดับนี้มาก Genmab ปรับ guidance ขึ้น 2 ครั้งในปี 2026 ทั้งฝั่ง royalty และ Epkinly ซึ่งเป็นการต่อยอด trend ที่เกิดขึ้นแล้ว ไม่ใช่ hope

**Verdict: Still underrated**

**Falsifying number:** Genmab FY2026 total revenue (guidance $4.3-4.5B, midpoint $4.4B, raised from 14%→19% growth, call l.10) รายงานต่ำกว่า **$4.3B** (bottom ของ guided range) ใน FY2026 full-year results (คาด ~ก.พ. 2027 ตามจังหวะ H1/FY-only ที่ transcript ยืนยัน — Genmab ไม่รายงานรายไตรมาสแบบ Q3, การรอ "Q3 2026" ที่ agent บางตัวเสนอมาจึงผิด cadence) นี่เป็น full-period target ที่ตัดสินได้แค่ตอนนั้นเท่านั้น

*Integrator note: valuation/sentiment agent ทั้งคู่เสนอ falsifier แบบ "Q3 2026 Darzalex royalty growth <10% YoY" — ผมแก้เป็น FY2026 revenue guidance miss เพราะ transcript เองยืนยันว่า Genmab report เป็น H1/FY เท่านั้น ไม่มี "Q3" ให้ดู*

## Variant Perception

- *Thesis metric:* **Darzalex royalty growth rate (ไม่ใช่ J&J's net trade sales) คู่กับ Epkinly/Tivdak revenue mix** — royalty growth บอกว่า core annuity ยังแข็งก่อนถึง cliff, mix บอกว่า diversification ไปถึงไหนแล้วจริง
- *Where we differ from consensus:* nothing — we hold the consensus view (6 Buy/1 Hold, avg PT $40.40, web UNVERIFIED) สิ่งที่เราเฝ้าเพิ่มคือ **management ไม่เคยพูดถึง patent cliff/Faspro บน call เลย** ซึ่งเป็น risk ที่ sell-side พูดถึง (patent cliff 2029) แต่ Genmab เองไม่ address — ถ้า silence นี้กลายเป็น pattern ต่อเนื่องหลาย call จะเป็นสัญญาณที่ควรถาม IR ตรงๆ

## Kill Conditions

Thesis: *Darzalex royalty เป็น high-margin annuity ที่ยังโตอยู่ ให้เวลา Genmab build Epkinly/petosemtamab/Rina-S ให้ใหญ่พอทดแทนก่อนถึง 2029 cliff*

- **US patent cliff 2029 มาถึงพร้อม Faspro รักษา volume ได้น้อยกว่า 70-80% ที่ประเมินไว้ (UNVERIFIED) และ management ไม่เคย address ความเสี่ยงนี้บน call แม้แต่ครั้งเดียว** — ไม่มี floor ที่ชัดเจนเพราะยังไม่มีตัวเลขจริงจากฝ่ายบริหาร `[open-ended]`
- **Epkinly frontline DLBCL (EPCORE DLBCL-2 interim, Q4 2026) หรือ petosemtamab head/neck readout ผิดหวัง** ขณะที่ diversification thesis พึ่ง readout กลุ่มนี้อยู่ — Epkinly+Tivdak ~$396M จาก H1 revenue $2.05B (~19%) `[bounded ~20%]`
- **FY2026 revenue ปิดต่ำกว่า guidance floor $4.3B** เมื่อรายงาน (~ก.พ. 2027) — สัญญาณว่าทั้ง royalty และ pipeline โตช้ากว่าที่ปรับ guidance ไว้ `[bounded ~15%]`
- **Merus debt ($5.5B, UNVERIFIED) เจอ readout กลุ่ม Q4 2026/Q1 2027 (petosemtamab, Rina-S, Epkinly) พลาดพร้อมกันหลายตัว** — leverage บวกกับ binary event risk ที่ไม่มี dividend cushion `[open-ended]`

---

## What to Ask

1. **ทำไม management ไม่พูดถึง patent cliff/Faspro บน call เลย?** — ถามตรงใน call ถัดไปหรือ IR ว่า retention estimate 70-80% (web) เป็นตัวเลขที่บริษัทยอมรับหรือไม่ ถ้าไม่มีคำตอบต่อเนื่องหลาย quarter คือสัญญาณเตือน
2. **effective tax rate 3.6% จะ normalize ที่เท่าไหร่ใน 12-18 เดือนข้างหน้า** และกระทบ operating profit guidance แค่ไหนเมื่อ tailwind หมด?
3. **Merus debt $5.5B (UNVERIFIED) มี covenant หรือ maturity ที่ผูกกับ readout ไหนไหม?** ถ้า petosemtamab/Rina-S พลาดพร้อมกัน จะกระทบความสามารถ refinance หรือไม่

---

*ไม่ใช่คำแนะนำการลงทุน — research summary จาก H1 2026 earnings call (local source เดียว) และ agent web research (UNVERIFIED ตามที่ label)*

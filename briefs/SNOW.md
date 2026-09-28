---
ticker: SNOW
company: Snowflake
updated: 2026-09-26
type: stock-brief
shared_driver: enterprise-software
---

# SNOW — Snowflake Inc.
**Date:** 2026-09-26 | *Refresh of the 2026-09-18 brief via /deep — adds Q2 FY2027 call, debate round, valuation verdict, variant perception, damage-tagged kill conditions. Price $335.94 (yfinance, 2026-09-26)*

**Source docs:** [[sources/SNOW/10-k-fy2026]] · [[sources/SNOW/q2-2027-call]]

---

## Company Snapshot

Snowflake คือ "AI Data Cloud" — consumption-based platform (จ่ายตาม compute/storage/data transfer จริง ไม่ใช่ fixed subscription) รันอยู่บน multi-cloud infrastructure ของ [[AMZN]], [[MSFT]] และ Google Cloud *(fundamentals agent, 10-K l.1100)* FY2026 (ปีบัญชีสิ้นสุด 31 ม.ค. 2026) revenue $4.68B โตต่อเนื่อง 29% ทั้งจาก $3.63B และ $2.81B ปีก่อนหน้า *(fundamentals; 10-K l.946,1084,1088)*

จุดที่เปลี่ยนไปจาก brief เดิม: Q2 FY2027 (ไตรมาสสิ้นสุด ก.ค. 2026) product revenue โต **เร่งขึ้น 3 ไตรมาสติด** (29%→37%) ขับเคลื่อนครึ่งหนึ่งโดย AI products (Cortex/CoCo/CoWork) *(earnings agent, q2-2027-call l.68,110)* — narrative เปลี่ยนจาก "NRR กำลังชะลอ" อย่างเดียว เป็น "NRR ชะลอ แต่ growth กลับมาเร่ง"

---

## Fundamentals Signal
*Source: fundamentals agent, sources/SNOW/10-k-fy2026.md (FY2026 = ปีบัญชีสิ้นสุด 31 ม.ค. 2026)*

**Revenue durability:** RPO $9.77B (46% แปลงเป็นรายได้ใน 12 เดือน, l.780,792) ลูกค้า >$1M TTM product revenue โต 576→733 (+27%, l.1100) คิดเป็น 68% ของ product revenue — กระจายพอสมควรภายใน segment ลูกค้าใหญ่ 790 Forbes Global 2000 = ~43% ของรายได้ (l.32,691) — concentration ยังมีแต่ไม่ single-customer risk NRR 125% ลดจาก 126%→133% ใน 2 ปี (l.771) และ 10-K เองบอกว่าจะลดต่อในระยะยาว (l.804)

**Margin trend:** Gross margin คงที่ 67% (product margin ขึ้น 71%→72%, l.1134,1138) **Operating loss ลดลงครั้งแรกใน 3 ปี:** $1.095B (FY24) → $1.456B (FY25) → **$1.435B (FY26)** — dollar loss เริ่มลดจริง ไม่ใช่แค่ % ดีขึ้น (l.963,1030) Net loss $1.33B, accumulated deficit $9.5B (ขึ้นจาก $7.3B, l.975,431) SBC ลดเหลือ 34% ของรายได้ (จาก 41%→42%, l.997,1064,1001) แต่ unvested SBC ค้างอีก $3.1B

**Capital allocation:** R&D $1.97B = 42% ของรายได้ ลดจาก 49% (l.1186,1192) ซื้อกิจการ 2 ดีลใน 9 เดือน — Crunchy Data $164.5M (มิ.ย. 2025) และ Observe ~$596M (ก.พ. 2026, เข้า FY2027) รวม >$750M (l.712,714) FCF $1.12B (+27%, l.765,828-833) **ไม่มี buyback/dividend เลย**

---

## Latest Earnings — Q2 FY2027 (ไตรมาสสิ้นสุด ~31 ก.ค. 2026)
*Source: earnings agent, sources/SNOW/q2-2027-call.md*

- Product revenue **$1.49B (+37% YoY)**, total revenue $1.55B (+35%) — **เร่งขึ้น 3 ไตรมาสติด** จาก 29% (l.10,12,110)
- NRR 126% (l.14) ลูกค้า >$1M TTM 828 ราย (+27% YoY, +48 net new ไตรมาสนี้, l.24) net new customer +692 ราย (+32% YoY, l.28)
- RPO $9B (+30% YoY ไตรมาสนี้), 54% (~$4.9B) จะรับรู้ใน 12 เดือน (+42% YoY, l.16,18)
- AI adoption: CoCo (coding agent) 9,100+ accounts (+2,000 ไตรมาสนี้) CoWork (conversational query) 5,800 accounts — AI products ขับ ~50% ของ growth ที่เร่งขึ้น (l.30,32,68)
- Guidance ปรับขึ้น: FY2027 product revenue $6.07B (จาก $5.84B, +36%) non-GAAP operating margin ขึ้นเป็น 14.5% (จาก 13.5%, l.36,38) แต่ **product gross margin ถูกปรับลงเหลือ 74%** เพราะ AI/GPU workload margin บางกว่า core storage/compute (l.22)
- หุ้นตอบสนอง +2.09% วันเดียว ปิดที่ $339.39 (l.365-366)

*หมายเหตุ integrator: brief เดิม (18 ก.ย.) อ้างว่ามี "$6B AWS deal ใหม่" และหุ้นพุ่ง 29% ไตรมาสนี้ — grep ทั้งไฟล์ transcript แล้วไม่พบทั้งสองข้อความนี้ จึงตัดออก ไม่ carry-forward ตัวเลขที่ยืนยันไม่ได้*

---

## Bull / Bear

**Bull** *(bull_researcher)*

- **Switching costs + Process power:** 97% ของรายได้อยู่ใน capacity contract, NRR 125-126% คือลูกค้าใช้มากขึ้นจริงไม่ใช่แค่อยู่ต่อ — NRR ที่ลดลงจาก 133%→125% เป็นผลทางคณิตศาสตร์ของฐานที่ใหญ่ขึ้น ไม่ใช่ลูกค้าหนี ขณะที่ product gross margin ขึ้น 71%→72% และ operating margin ดีขึ้นจริง (-40%→-31%) — process power เริ่มปรากฏในตัวเลข ไม่ใช่แค่ story *(10-K l.771,1138,1030; q2-call l.14,24,110)*
- **Cornered resource ด้าน AI distribution:** ดีล OpenAI $200M (ใหญ่กว่า Databricks 2 เท่า) บวก CoCo 9,100+ accounts และ CoWork 5,800 accounts — AI ขับ ~50% ของ growth ที่เร่งขึ้นเอง ไม่ใช่ story แยกจาก core platform *(sentiment; q2-call l.30,32,68)*
- **Rule of 40 ผ่านแล้ววันนี้ ไม่ใช่สัญญา:** 37% growth + ~24% FCF margin ≈ 61 บวก guidance ที่ปรับขึ้นทั้ง revenue และ margin ในไตรมาสเดียวกับที่ AI margin โดนกดลง — management แลก known margin headwind กับ top-line ที่เร่งขึ้น และตลาดให้รางวัล *(valuation agent; q2-call l.22,36,38)*
- **Concentration ที่ดูน่ากลัวแท้จริงกระจายในลูกค้าใหญ่:** 790 G2000 = 43% ของรายได้ แต่ใน cohort นั้น >$1M customers โต 27% เป็น 828 ราย กระจาย 68% ของ product revenue — land-and-expand ไม่ใช่ single-point-of-failure *(10-K l.1100; q2-call l.24)*

**Bear** *(bear_researcher)*

- **Growth กำลังชะลอและกระจุกตัว ไม่ใช่ "reaccelerate" แท้จริง:** NRR 133%→126%→125% ใน 3 ปี และ 10-K เองบอกจะลดต่อระยะยาว (l.771,804) — Q2 FY27 ที่ NRR 126% ยังต่ำกว่าฐาน 133% เมื่อ 2 ปีก่อน เป็นแค่อัตราชะลอที่ช้าลง ไม่ใช่กลับตัว **bull ไม่มีคำตอบต่อ trend ของ NRR เอง** มีแต่ตัวเลข product revenue ไตรมาสเดียว
- **AI narrative มาพร้อมต้นทุน margin และ GAAP loss ยังโตเป็นตัวเงิน:** product gross margin ถูกปรับลงเหลือ 74% เพราะ Cortex/GPU margin บางกว่า (l.22) ตัวขับ growth ที่ bull ชูคือตัวกัดกร่อน margin เดียวกัน operating loss ตัวเงินแทบไม่ลด 3 ปีติด ($1.095B→$1.456B→$1.435B) net loss $1.33B, accumulated deficit จาก $7.3B→$9.5B ใน 1 ปี (l.963,975,431) ไม่มี capital return เลย
- **M&A ที่ยังพิสูจน์ไม่ได้:** 2 ดีลใน 9 เดือน (Crunchy Data + Observe รวม >$750M) ไม่มี track record integration เปิดเผย (l.712,714)
- **Valuation ราคาไว้กับ 10 ปีของ execution ที่สมบูรณ์แบบ ท่ามกลางคู่แข่งที่โตเร็วกว่าและทุนหนากว่า — จุดนี้ bull ไม่มีคำตอบ:** Forward EV/Sales ~17.9x, EV/FCF ~102x ต้องการ FCF โตเกือบ 3 เท่าและ revenue โต mid-20s%+ ต่อเนื่องราวหนึ่งทศวรรษ ขณะที่ Databricks โต 65-80% เทียบ SNOW 29-37% ด้วย valuation เอกชนสูงกว่า (~$190B vs ~$114B) Barclays downgrade แล้วเพราะ valuation ตึง และหุ้นขึ้นมา 47-50% YTD แล้ว *(valuation agent; sentiment, UNVERIFIED)*

---

## Valuation

*Lens: EV/Sales เทียบกับ growth+margin trajectory, cross-check ด้วย Rule of 40 (growth% + FCF margin%) — P/E ใช้ไม่ได้เพราะยังขาดทุน GAAP (valuation agent)*

Market cap ~$114B (UNVERIFIED, web) ÷ FY2027 guided revenue ~$6.36B ≈ **forward EV/Sales 17.9x** — Rule of 40 วันนี้: 37% growth + ~24% FCF margin ≈ 61 ผ่านเกณฑ์แล้ว Forward EV/FCF ~102x บีบให้เหลือระดับสมเหตุสมผล (~25-30x) ได้ก็ต่อเมื่อ FCF โตเกือบ 3 เท่าใน 2-3 ปีข้างหน้า — ราคาต้องการ **mid-20s%+ revenue CAGR ต่อเนื่องราวหนึ่งทศวรรษ** บวก FCF margin ขยับจาก ~24% ไปสู่ ~30%+ ซึ่งอยู่ *ที่หรือต่ำกว่า* ที่ SNOW เพิ่งพิสูจน์แล้ว (37% growth, guide 36%) ไม่ใช่การก้าวกระโดดที่ยังไม่พิสูจน์

**Verdict: Deserved**

**Falsifying number:** Q3 FY2027 (ไตรมาสสิ้นสุด ~31 ต.ค. 2026, รายงานผลราวปลาย พ.ย. 2026) product revenue growth ต่ำกว่า 30% YoY หรือ NRR หลุดต่ำกว่า 123%

*Integrator note: bear ชี้ถูกว่า "Deserved" วางอยู่บนสมมติฐานว่าไตรมาสที่เร่งขึ้น 3 ไตรมาสติดเป็น trend ไม่ใช่ beat-and-raise ครั้งเดียว — Q3 FY2027 คือจุดพิสูจน์จริง*

---

## Variant Perception

- *Thesis metric:* **Product revenue growth YoY คู่กับ NRR** — growth บอกว่า reacceleration ยังไปต่อ, NRR บอกว่าฐานลูกค้าเดิมยังขยายใช้งานจริงไม่ใช่แค่ลูกค้าใหม่ชดเชยลูกค้าเก่า
- *Where we differ from consensus:* nothing — we hold the consensus view (Strong Buy ~43/50, PT เฉลี่ย ~$370-413, web UNVERIFIED) สิ่งที่เราเฝ้าเพิ่มคือ **สัดส่วนของ growth ที่เร่งขึ้นที่มาจาก AI/Cortex จริง ๆ เทียบกับ core consumption** — บริษัทบอกแค่ "~50%" แบบกว้าง ไม่แยกละเอียด

---

## Kill Conditions

Thesis: *Snowflake เป็น platform ที่ enterprise data ฝังตัวอยู่แล้ว (switching costs) และ AI adoption กำลัง compound เป็น growth ที่เร่งขึ้นจริง ไม่ใช่แค่ hype รอบเดียว*

- **NRR หลุดต่ำกว่า 122% ต่อเนื่อง 2 ไตรมาส** — ต่ำกว่าที่ trend ปัจจุบัน (125-126%) ควรจะเป็น แปลว่าฐานลูกค้าเดิมหยุดขยายใช้งานเร็วกว่าที่คาด `[bounded ~40%]`
- **Product revenue growth ร่วงกลับต่ำกว่า 25% YoY ต่อเนื่อง 2 ไตรมาส** — พิสูจน์ว่าการเร่งขึ้น 29%→37% เป็น beat-and-raise ครั้งเดียว ไม่ใช่ trend ที่ valuation ต้องการ `[bounded ~45%]`
- **GAAP/non-GAAP operating margin หยุดดีขึ้นหรือถอยหลัง** ใน 2 ปีบัญชีข้างหน้า (ไม่ narrow ต่อจาก -31% FY26) ทั้งที่ไม่มี capital return และ accumulated deficit โตต่อ — แปลว่า reinvestment ไม่ compound เป็น operating leverage จริง `[bounded ~35%]`
- **Databricks (หรือคู่แข่ง AI-native อื่น) ชนะ market share ใน AI-native workload อย่างเด็ดขาด** — Databricks โต 65-80% เทียบ SNOW 29-37% ด้วยทุนเอกชนหนากว่า Snowflake ติดอยู่แค่ "serving layer" ตลอดไป `[open-ended]`

*Loosened/removed 2026-09-26: ตัดเงื่อนไข "Crunchy Data/Observe ไม่ integrate สำเร็จภายใน 12-18 เดือน" ออกจาก kill conditions — มูลค่ารวม >$750M เทียบ market cap ~$114B (<1%) ไม่ถึงระดับ thesis-breaking ตาม threshold ของ skill (≥50% หรือ open-ended) ย้ายไปเป็นแค่ bear point แทน และ tighten เงื่อนไข NRR จาก "หลุดต่ำกว่า 120%" เป็น "หลุดต่ำกว่า 122% ต่อเนื่อง 2 ไตรมาส" เพราะฐานปัจจุบันอยู่ที่ 125-126% แล้ว เหลือ room ให้ทรุดได้น้อยกว่าที่คิดตอนเขียนครั้งก่อน และแทนที่เงื่อนไข GAAP loss แบบกว้าง ๆ ด้วยตัวเลขที่ชัดขึ้น (operating margin หยุดดีขึ้นภายใน 2 ปี) เพราะ FY26 เพิ่งแสดง margin ดีขึ้นครั้งแรกใน 3 ปี*

---

## What to Ask

1. **Product revenue growth 37% ใน Q2 FY27 จะยืนได้กี่ไตรมาส?** นี่คือจุดพิสูจน์ทั้งหมดของ "Deserved" — ถ้า Q3 FY27 หลุดต่ำกว่า 30% แปลว่าเป็น beat ครั้งเดียว ไม่ใช่ trend
2. **AI/Cortex ที่ขับ ~50% ของ growth ที่เร่งขึ้น แยกเป็นรายได้จริงเท่าไหร่?** บริษัทให้แค่ตัวเลข accounts (9,100+ CoCo, 5,800 CoWork) ไม่ใช่ revenue contribution ที่ชัดเจน
3. **Operating margin ที่ดีขึ้นครั้งแรกใน 3 ปี (FY26) จะดีขึ้นต่อเนื่องไหม?** หรือเป็นแค่ one-off จาก SBC ที่ลดลง — ต้อง track ว่า non-GAAP operating margin guide 14.5% จะทำได้จริงและขยับต่อในปีถัดไปหรือไม่

---

*ไม่ใช่คำแนะนำการลงทุน — research summary จาก 10-K FY2026, Q2 FY2027 call และ agent analysis*

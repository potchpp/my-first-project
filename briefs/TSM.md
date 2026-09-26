---
ticker: TSM
company: Taiwan Semiconductor Manufacturing
updated: 2026-09-26
type: stock-brief
shared_driver: ai-capex
---

# TSM — Taiwan Semiconductor Manufacturing Co.
**Date:** 2026-09-26 | *Refresh via /deep — adds Q2 2026 call, debate round, valuation verdict, variant perception, damage-tagged kill conditions. Price $450.61 (Yahoo, 2026-09-26). No 20-F on file (fetch_10k.py only pulls 10-K) — annual figures and EPS estimates are UNVERIFIED (web)*

**Source docs:** [[sources/TSM/q2-2026-call]]

---

## Company Snapshot

TSMC เป็นโรงงานผลิต chip แบบรับจ้างล้วน (pure-play foundry) — ผลิตให้ [[NVDA]], [[AAPL]], [[AMD]], [[AVGO]] และแทบทุกบริษัทที่ออกแบบ chip เอง ไม่มีสินค้าของตัวเองแข่งกับลูกค้า HPC/AI เป็น 66% ของรายได้แล้ว และ node 7nm ลงไปเป็น 77% ของรายได้ wafer *(earnings agent, q2-2026-call l.16-18)*

## Fundamentals Signal

- **Revenue durability: สูงใน HPC** — ลูกค้า design-in หลายปีต่อ node และผู้บริหารบอกว่าการย้าย fab ไม่มีทางลัด; ลูกค้ากระจุกตัว (ยอมรับเองว่าเป็นธรรมชาติของช่วง AI) *(fundamentals agent)*
- **Margin trend: สูงแต่กำลังถูก dilute ตามแผน** — GM 67.7% ใน Q2; N2 ramp กด GM 3-4 จุดใน H2 และ fab ต่างประเทศกด 2-3 จุด ขยายเป็น 3-4 จุดในระยะยาว *(q2-2026-call l.40-42)*
- **Capital allocation: reinvest + ปันผล** — capex 2026 $60-64B (จาก $52-56B), Arizona เพิ่มอีก $100B, ปันผล NT$24 (+33%), ไม่มี buyback *(l.30-34)*

## Latest Earnings — Q2 2026

- Revenue **$40.2B (+33.7% USD)** (l.10, verified); net income +77.4%; GM 67.7% (+150bps QoQ)
- Platform: HPC 66% (+20% QoQ), smartphone 22%, IoT 5%, auto 4%; node: N5 33%, N3 30%, N2 3% *(l.16-20)*
- Q3 guide $44.6-45.8B, GM 65-67%, operating margin 56-58% (l.24-26, verified); **ปี 2026 คาดโต "มากกว่า 40% เล็กน้อย"** (l.28, verified)
- A14 ตามแผนผลิตจริงปี 2028; ทุกสถาปัตยกรรม CPU (x86, Arm, RISC-V) เป็นลูกค้าหลักของ TSMC *(l.62, 70-72)*
- **Web (unverified):** รายได้ ส.ค. NT$514.8B (+53.3% YoY); Section 232 ภาษี chip 25% โดยดีล Taiwan จำกัดที่ 15%; Arizona Fab 21 เฟส 2 ผลิตจริง Q1 2027 เร็วกว่าแผน; CoWoS 125-130k wafer/เดือนปลายปี, NVIDIA จองไว้ ~60% *(sentiment agent)*

## Bull / Bear

**Bull** *(bull_researcher)*
- **Process power:** เรียนรู้ node ใหม่ก่อนทุกคนและทำ yield ได้ — A14 test vehicle yield 90% บน SRAM 256Mb *(earnings agent l.70-72)*
- **Switching costs ที่ผู้บริหารพูดเอง + cornered resource ใน CoWoS:** ลูกค้าไม่มีที่อื่นให้ไปที่ node ที่ต้องการ; CoWoS คือคอขวดของทั้ง AI buildout *(fundamentals + sentiment agents)*
- **Pricing power จ่าย dilution ได้:** ขึ้นราคา 3-10% ในปี 2026 และ 15% บน N3 ใน H2 ขณะยัง guide GM 65-67% *(sentiment agent, unverified)*

**Bear** *(bear_researcher)*
- **Margin dilution ซ้อนกันสองชั้นและกว้างขึ้น:** N2 (−3-4 จุด) + ต่างประเทศ (−2-3 → −3-4 จุด) ในจังหวะที่ valuation ต้องการ GM กลาง 60s — **bear point ที่ไม่มี bull counter** เพราะการขึ้นราคาเป็นตัวเลขจาก web *(q2-2026-call l.40-42)*
- **Capex เพื่อป้องกันมากกว่าเพื่อโต:** Arizona $100B เพิ่มเป็นต้นทุนทางการเมืองที่ margin ต่ำกว่า Taiwan *(l.30-32)*
- **Concentration สองชั้น:** HPC 66% ของรายได้ และ NVIDIA จอง ~60% ของ CoWoS — ลูกค้าไม่กี่รายกำหนดชะตาทั้ง AI cycle *(earnings + sentiment agents)*
- *Integrator note:* ข้อดีเรื่องภาษีและ Arizona ขึ้นอยู่กับนโยบาย — นักลงทุนเลี่ยง thesis ที่พึ่ง macro/นโยบาย และความเสี่ยง Taiwan ยังเป็นเงื่อนไขที่ไม่มีพื้น

## Valuation

*Lens: forward P/E เทียบกับ growth, cross-check EV/EBITDA เพราะ capex หนัก (valuation agent)*

ราคา $450.61 ≈ 28x EPS 2026E ~$15.91 และ ~26x 2027E ~$17.32 (UNVERIFIED, web) ราคานี้ต้องการรายได้โตระดับ high-30s ถึง low-40s% และ GM กลาง 60s — ซึ่งเป็นสิ่งที่ guide ไว้แล้ว (l.26, 28, verified)

**Verdict: Deserved**

**Falsifying number:** รายได้ทั้งปี 2026 (USD) โตต่ำกว่า ~35% YoY เมื่อรายงาน Q4 2026 (ม.ค. 2027) เทียบกับ guide "มากกว่า 40% เล็กน้อย"

## Variant Perception

- *Thesis metric:* **GM หลัง dilution** — ต้องอยู่ ≥65% ขณะ N2 + overseas ramp; และ **HPC revenue growth QoQ**
- *Where we differ from consensus:* nothing — we hold the consensus view ข้อควรระวังเพิ่มคือ multiple ตั้งอยู่บน EPS estimate จาก web ที่ยังไม่ได้ verify กับ 20-F

## Kill Conditions

- **Taiwan geopolitical escalation อย่างมีนัยสำคัญ** (blockade, military action) — impact รุนแรงทันทีเพราะ capacity กระจุกใน Taiwan >90% `[open-ended]`
- **Top customer ([[AAPL]] / [[NVDA]]) ชะลอ capex/order อย่างมีนัยสำคัญ** — 58% ของรายได้อยู่ที่ 5 ราย `[bounded ~40%]`
- **Gross margin ลดเกินที่ guide ไว้ 3-4 จุด หรือไม่ฟื้นหลัง 2H26** — overseas dilution รุนแรงกว่าคาด `[bounded ~25%]`
- **Arizona/overseas fab profitability พลิกกลับเป็นลบ** — geographic diversification ไม่ sustainable `[bounded ~20%]`
- **ลูกค้าหลักประกาศ qualify foundry รายที่สองที่ leading-edge node (2nm หรือต่ำกว่า)** — switching cost thesis แตกตรงๆ `[bounded ~50%]`

*Tightened 2026-09-26: added dual-sourcing condition from the bull round. The two gross-margin and Arizona conditions are below 50% damage on their own and belong in Bear, but are kept as written — not loosened.*

## What to Ask

1. **N2 dilution 3-4 จุดจะหายไปเมื่อไหร่ในอดีต?** ดูว่า N3 และ N5 ใช้กี่ไตรมาสกว่าจะกลับมาที่ corporate average — ใช้เป็นเกณฑ์วัด N2
2. **ต้องหา 20-F FY2025 มาเก็บใน sources/TSM/** เพื่อ verify EPS, customer concentration (ตัวเลข 58% ที่ top 5 และ Apple 25% มาจาก brief เดิมที่ใช้ web) ก่อนเชื่อ multiple 28x
3. **NVIDIA ~60% ของ CoWoS แปลว่า [[AMD]] และ [[AVGO]] ได้ capacity เท่าไหร่?** ถ้า CoWoS ยังตึง TSMC เลือกได้ว่าใครโต — นั่นคือ pricing power หรือ concentration risk

---

*ไม่ใช่คำแนะนำการลงทุน — research summary จาก Q2 2026 call และ agent analysis (annual figures = web, unverified)*

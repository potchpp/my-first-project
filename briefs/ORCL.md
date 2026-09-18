# ORCL — Oracle Corporation
**Date:** 2026-09-18 | **Sources:** sources/ORCL/10-k-fy2026.md + web research (sentiment agent) | *No earnings transcript available*

---

## Company Snapshot

Oracle ขาย enterprise IT สามส่วน: Cloud and software (87% ของรายได้), Hardware (5%), Services (8%) FY26 revenue $67.357B (+17%) engine หลักคือ **OCI (Oracle Cloud Infrastructure)** ที่ตอนนี้คิดเป็น 53% ของ cloud revenue (จาก 35% เมื่อ 2 ปีก่อน) — shift ไป OCI เร็วมาก

จุดเปลี่ยนที่ใหญ่ที่สุด: **OpenAI ผูกพัน $300B ตลอด 5 ปี** (เริ่ม 2027, ~$60B/ปี) ต้องการ power capacity 4.5GW — เป็นทั้ง demand validation ก้อนใหญ่ที่สุด และ concentration risk ที่ใหญ่ที่สุดพร้อมกัน (roughly ครึ่งหนึ่งของ contracted revenue ทั้งหมด $638B ผูกกับลูกค้ารายเดียว)

---

## Fundamentals Signal
*Source: sources/ORCL/10-k-fy2026.md (MD&A only — ไม่มี balance sheet/customer concentration disclosure ในไฟล์นี้)*

**Revenue durability — โตเร็ว แต่ concentration สูงมาก:** Cloud+software +19%, OCI ขับเคลื่อน 84% ของ cloud growth ทั้งหมด สัญญา cloud เป็น subscription 1-5 ปี (recurring base) — แต่ไฟล์นี้ไม่มีตัวเลข RPO หรือ customer concentration ให้อ้างอิงตรงๆ

**Margin trend — กำลังโดนกดดันจาก OCI buildout:** margin % ของ cloud/software **ลดลง** (constant currency) เพราะ "infrastructure expenses เพิ่มขึ้นเพื่อรองรับการเติบโตของ cloud infrastructure" opex เพิ่ม $7.0B (ส่วนใหญ่ $6.0B มาจาก infra cost)

**Capital allocation — reinvest หนักมาก, ทุนมาจากหนี้:** Capex $55.7B ในปีเดียว fund ด้วย $42.7B senior notes + $5.0B mandatory convertible preferred stock — เกือบทั้งหมดมาจากหนี้/hybrid instrument Buyback แค่ $95M เทียบ dividend $5.8B — คืนทุนผู้ถือหุ้นน้อยมาก เงินเกือบทั้งหมดไปที่ infrastructure

---

## Latest Earnings
*Source: sentiment agent — no transcript in sources/ORCL/*

Q1 FY26: Revenue +11% เป็น $14.9B, cloud +27% เป็น $7.2B, **OCI +54% เป็น $3.3B**, consumption +57% **RPO backlog พุ่ง 359% เป็น $455B** ต่อมารายงานใกล้ $664B

OpenAI commit $300B/5 ปี (เริ่ม 2027 ~$60B/ปี — มากกว่า revenue ปัจจุบันของ OpenAI เองที่ ~$10B) ลูกค้า cloud รายอื่น: xAI, Meta, Nvidia, AMD

---

## Bull / Bear

**Bull**

- **Counter-positioning:** ขณะที่ AWS/Azure/GCP สร้าง general-purpose cloud ก่อนแล้วค่อยเพิ่ม AI capacity, Oracle ออกแบบ OCI เพื่อ AI workload โดยเฉพาะตั้งแต่แรก — OCI ขับเคลื่อน 84% ของ cloud growth และ share พุ่งจาก 35%→53% ใน 2 ปี
- **Switching costs:** $58.53B (87% ของรายได้) อยู่บน subscription 1-5 ปี — ลูกค้าผูกสัญญา capacity หลายปี ไม่ใช่ pay-as-you-go
- **Cornered resource:** RPO backlog $455-664B คือ demand ที่ Oracle **ถือสัญญาแล้ว** OpenAI deal ต้องการ power 4.5GW — พิสูจน์ว่า Oracle secure capacity (power, chip, buildout) ที่คู่แข่งตามไม่ทันเร็ว xAI/Meta/Nvidia/AMD ก็ใช้ OCI — ไม่ใช่แค่ favor ให้ OpenAI รายเดียว

**Bear**

- **Margin กำลังแตกจริง:** cloud/software margin % ลดลงเพราะ infra cost โตเร็วกว่า revenue — buildout ยังไม่จ่ายตัวเองคืนได้
- **Financing มาจากหนี้เกือบทั้งหมด:** capex $55.7B fund ด้วย debt/preferred $47.7B ผู้ถือหุ้นได้ buyback แค่ $95M — capital discipline หายไป equity holder อยู่ท้ายแถว
- **Concentration risk มหาศาล:** ~ครึ่งของ $638B backlog ผูกกับ OpenAI รายเดียว ที่ revenue ปัจจุบันแค่ ~$10B เทียบ obligation $60B/ปี debt-to-equity 427% (เทียบ Microsoft 32.7%) S&P ปรับ credit rating ลงเหลือ BBB- (ห่าง junk แค่ 1 notch) Q1 FCF ติดลบ $5.4B ยังต้องการเงินเพิ่มอีก ~$40B

---

## Kill Conditions

- **OpenAI ผิดนัดชำระหรือ renegotiate สัญญาลงอย่างมีนัยสำคัญ** — เพราะ concentration สูงมาก impact จะรุนแรงทันที
- **Credit rating ถูก downgrade เข้า junk** — จะทำให้ cost of funding เพิ่มขึ้นอีกในช่วงที่ยังต้องกู้เพิ่ม
- **Cloud/software margin ลดลงต่อเนื่อง 2+ ไตรมาสติด** โดยไม่เห็นสัญญาณว่า infra cost จะ stabilize
- **Free cash flow ติดลบต่อเนื่องเกิน 3-4 ไตรมาส** โดยไม่มี debt reduction plan ชัดเจน

---

## What to Ask

1. **ถ้า OpenAI ประสบปัญหา solvency จริง Oracle มี contractual protection อะไรบ้าง?** (deposit, minimum commitment penalty, capacity ที่ resell ให้ลูกค้าอื่นได้ไหม)
2. **แผน deleverage หลัง buildout รอบนี้เป็นยังไง?** debt-to-equity 427% ต้องมี exit plan ไม่งั้นความเสี่ยง credit downgrade จะคงอยู่นาน
3. **ลูกค้า cloud รายอื่น (xAI, Meta, Nvidia, AMD) มีขนาด commitment เทียบกับ OpenAI แค่ไหน?** จะบอกได้ว่า diversification จริงมีมากแค่ไหนนอกเหนือจาก headline

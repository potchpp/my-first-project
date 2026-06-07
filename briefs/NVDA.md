# NVDA — NVIDIA Corporation
*Brief generated: 2026-06-07 | Sources: sources/NVDA/10-k-fy2026.md (FY2026, period ending Jan 25, 2026)*
*Note: ไม่มี earnings call transcript ใน sources/NVDA/ — fetch_transcript.py ไม่พบ URL บน Motley Fool*

---

## What the company does

NVIDIA ออกแบบ GPU และ AI computing platform ที่กลายเป็น infrastructure หลักของ AI revolution — ตั้งแต่ training โมเดลขนาดใหญ่ไปจนถึง inference ใน data center ทั่วโลก บริษัทมีสองส่วนหลักคือ Compute & Networking (Data Center, Automotive) และ Graphics (GeForce gaming, RTX PRO workstation) โดย Data Center เป็น engine ที่ใหญ่ที่สุดและโตเร็วที่สุด CUDA software ecosystem ที่สะสมมากว่า 20 ปีและ developer base 7.5 ล้านคนทั่วโลกเป็น switching cost ที่ลึกที่สุดในวงการ — นักพัฒนา AI เขียนโค้ดบน CUDA ก่อน แล้วจึงคิดเรื่อง hardware ทีหลัง

---

## Latest earnings — FY2026 Full Year (period ending Jan 25, 2026)

> **หมายเหตุ:** ข้อมูลต่อไปนี้มาจาก 10-K FY2026 (full year) ไม่ใช่ quarterly transcript — ตัวเลขรายไตรมาสล่าสุดต้องตรวจสอบกับ earnings release จริง *(source: sources/NVDA/10-k-fy2026.md)*

- **Revenue $215.9B (+65% YoY)** — Data Center up 68%, Gaming up 41%, Professional Visualization up 70%, Automotive up 39%; ทุก segment โตสองหลักขึ้น *(source: sources/NVDA/10-k-fy2026.md)*
- **Gross margin 71.1% (ลดจาก 75.0%)** — ลดลง 3.9 pp เพราะ product transition จาก Hopper HGX ไป Blackwell full-scale datacenter solutions และ $4.5B H20 China charge *(source: sources/NVDA/10-k-fy2026.md)*
- **Net income $120.1B (+65% YoY), EPS $4.90 (+67% YoY)** — EPS โตเร็วกว่า revenue สะท้อน operating leverage *(source: sources/NVDA/10-k-fy2026.md)*
- **H20 China ban — $4.5B charge** — USG กำหนดให้ต้องมี license ส่ง H20 ไป China; Blackwell Ultra (GB300) เริ่ม ship Q2 FY2026; Rubin platform คาดเริ่ม production H2 FY2027 *(source: sources/NVDA/10-k-fy2026.md)*
- **R&D investment $76.7B cumulative since inception** — ลงทุน $17.5B ใน private companies และ infrastructure funds ใน FY2026 เพียงปีเดียว *(source: sources/NVDA/10-k-fy2026.md)*

---

## Bull case / Bear case

**Bull**
- **Process Power จาก CUDA สะสม 20+ ปี** — developer 7.5 ล้านคนเขียนบน CUDA; library, framework, toolchain ทั้งหมด optimize มาสำหรับ NVIDIA; switch ไป AMD หรือ custom chip = ต้นทุน migration สูงมาก *(source: sources/NVDA/10-k-fy2026.md)*
- **Full-stack platform ที่ extend ได้ทุก layer** — จาก GPU chip ไปถึง NVLink interconnect, DPU, networking, CUDA-X libraries, AI Enterprise software, NIM inference microservices — ทุก layer เพิ่ม lock-in และ revenue stream *(source: sources/NVDA/10-k-fy2026.md)*
- **Rubin platform + one-year cadence** — NVIDIA ขยับ product cycle เป็น annual แปลว่าคู่แข่งต้องไล่ตาม gap ที่กว้างขึ้นทุกปี *(source: sources/NVDA/10-k-fy2026.md)*

**Bear**
- **Gross margin กำลังลด** — 71.1% ใน FY2026 ลดจาก 75% ใน FY2025 เพราะ product transition และ China charge — ถ้า margin ลดต่อเนื่องทุก generation ที่ซับซ้อนขึ้น thesis เรื่อง compounding margin จะต้องทบทวน *(source: sources/NVDA/10-k-fy2026.md)*
- **China export control ยังไม่จบ** — H20 ถูก ban, H200 ได้ license บางส่วนแต่ต้อง inspect ใน US และติด 25% tariff — China เป็น market ใหญ่ที่ถูกตัดออกอย่างถาวรหรือบางส่วน *(source: sources/NVDA/10-k-fy2026.md)*
- **Hyperscaler in-house XPU กำลัง mature** — 10-K ระบุว่า NVIDIA เปิด NVLink Fusion ใน FY2026 ให้ hyperscaler integrate custom CPU/XPU กับ NVIDIA platform — แปลว่า hyperscaler บางส่วนกำลัง build custom chip แล้วจริง *(source: sources/NVDA/10-k-fy2026.md)*

---

## What to ask before owning it

1. Gross margin ลดจาก 75% → 71% ใน FY2026 — Rubin (FY2027) จะ stabilize หรือลดต่อ? ถ้า full-scale datacenter solutions มี margin ต่ำกว่า HGX เดิม trajectory ระยะ 3 ปีเป็นอย่างไร?
2. CUDA switching cost จะยืนได้นานแค่ไหนถ้า AMD ROCm หรือ open-source alternative สุกพอ — developer จะ migrate หรือ CUDA network effect แข็งแกร่งพอที่จะ hold?
3. ถ้า hyperscaler in-house XPU (TPU, Trainium, MTIA) จัดการ inference ส่วนใหญ่ได้เอง NVIDIA จะยังครอง training market ได้ไหม — training market ใหญ่พอไหมที่จะ justify valuation ปัจจุบัน?
4. China market หายไปถาวรหรือแค่ชั่วคราว — ถ้า ban ขยายต่อไปถึง Rubin จะ addressable market ลดลงแค่ไหน?

---

*ไม่ใช่คำแนะนำการลงทุน — research summary อิงจาก 10-K จริง; ไม่มี earnings call transcript สำหรับ NVDA*

# Project: My First Project

**What this is:** My first project เพื่อหัดใช้ Claude Code ใช้เป็นที่ทดลองสร้าง slash command, skill, sub-agent (always think of model it should use then if easy tasks, use cheaper token models)

## วิธีทำงาน

- ก่อนทำอะไรที่แก้ไฟล์เยอะหรือลบของ ให้ขออนุญาตก่อน
- แก้ไฟล์ที่มีอยู่แล้ว อย่าสร้างใหม่ถ้าไม่จำเป็น
- คำตอบให้ตรง อย่าอ้อม
- ภาษาไทยใช้ได้ ภาษาอังกฤษใช้ได้

## What lives where

- `briefs/` สำหรับ stock brief ที่ /brief สร้าง
- `.claude/commands/` สำหรับ slash command files
- `data/entity-types.json` คือ cache ที่บอกว่าแต่ละ entity ในกราฟเป็น company / product / person / risk ฯลฯ (สร้างครั้งเดียว ใช้ซ้ำได้ ไม่ต้อง rebuild กราฟ)
- `scripts/undercover.py` หา "หุ้นที่ยังไม่ได้ถือแต่ถูกพูดถึงในงานวิจัยของหุ้นที่ถืออยู่" — ตัวช่วยตอบคำถามข้อ 4 (มองข้ามตัวไหนใน supply chain ไปรึเปล่า)
  - รันด้วย `python3 scripts/undercover.py` | `--include-private` เพื่อดูบริษัทที่ไม่ได้จดทะเบียนด้วย
  - อ่านเฉพาะ `briefs/` กับ `graphify-out/` — **ไม่แตะ `portfolio/`** ข้อมูลส่วนตัวจึงไม่รั่ว
  - ถ้าเพิ่ม brief ใหม่แล้ว entity ใหม่ยังไม่ถูกจัดประเภท ให้ rerun graphify แล้ว classify เฉพาะ label ที่เพิ่มเข้ามา

## ห้าม

- อย่ารัน rm -rf หรือคำสั่งลบ folder โดยไม่ถามก่อน
- อย่าแก้ไฟล์ที่อยู่ข้างนอก folder นี้

## How I invest (voice for /brief output)

ผมลงทุนสไตล์ long-term (ถือ 2+ ปี) ทบทวนพอร์ตปีละ 2-3 ครั้ง ถ้าหุ้นตัวไหนผลติดลบและ thesis เปลี่ยนไปแล้ว ตัดออก ไม่ถือเพราะหวังว่าจะกลับมา

ผมเน้นบริษัทที่เป็น platform หรือ infrastructure ของอุตสาหกรรมที่กำลังเปลี่ยนโครงสร้าง ทั้งที่ established แล้วและที่กำลัง build อยู่ สนใจเป็นพิเศษกับธุรกิจที่อยู่ในจุดตัดระหว่างเทคโนโลยีกับอุตสาหกรรมเก่า ไม่ว่าจะเป็นวิถีของเมืองและวิถีชีวิต วิธีที่มนุษย์เดินทางและสำรวจ หรือวิธีที่คนดูแลสุขภาพตัวเอง ดู fundamentals ก่อนเสมอ revenue durability (รายได้มาจากลูกค้าซ้ำหรือต้องหาใหม่ตลอด?), margin trend (กำไรต่อบาทขายดีขึ้นหรือแย่ลง?), capital allocation (บริษัทเอากำไรไปทำอะไร ลงทุนต่อหรือแค่จ่ายปันผล?)

ผมยอมรับ volatility สูงได้ถ้า thesis ชัดและ addressable market ใหญ่พอ แต่เลี่ยงหุ้นที่เหตุผลซื้อขึ้นอยู่กับ Fed หรือ macro เพราะทำนายไม่ได้ ต้องการ kill condition ที่ชัดก่อนกดซื้อทุกครั้ง ถ้านึกไม่ออกว่าเมื่อไหร่ควรขาย แปลว่าผมยังไม่เข้าใจธุรกิจพอ

หลักที่ยึด: ทนความผันผวน แต่ไม่ทน fundamental ที่พัง — ตัดสินจากขนาดความเสียหายของธุรกิจ ไม่ใช่ % สีแดงบนจอ ถือผู้ชนะให้นานพอ ตัดผู้แพ้ให้เร็วพอ ขาย/ลดบางส่วนเพราะขนาด position หรือ valuation นำหน้าพื้นฐาน ไม่ใช่เพราะหุ้นขึ้นมาเยอะ หลาย ticker ที่พึ่ง driver เดียวกัน (เช่น AI capex) คือเดิมพันเดียว Conviction ต้องมี evidence รองรับ ไม่ใช่เพราะซื้อไปแล้ว

Skill `company-brief` ต้องสะท้อนเสียงนี้ใน output ทุกครั้ง ใน Bull/Bear, Kill conditions, และ "What to ask" sections โดยเฉพาะ

# outbreak_api
Automatic risk stratification, and recommendation for Thailand COVID19

** This is a proof of concept product and subject to change before being deploy. 
อยู่ระหว่างทดสอบขั้นต้นมากๆ อาจมีการปลี่ยนในอนาคต

# To-do list
- Support non-Thai recommendation
- Input validation
- Return รายชื่อประเทศกลุ่มเสี่ยง และปัจัยเสี่ยงอื่นๆ

# Input (JSON), please submit to /covid19 route only

fever: (numeric/float)
- คำถาม = มีไข้สูง 37.5 องศา (Celsius) ขึ้นไป หรือ รู้สึกว่ามีไข้ 
- ในกรณีรู้สึกว่ามีไข้ ให้ใส่ตัวเลข 37.5 
- Example : 37.55

one_uri_symp: (string "0"/"1")
- คำถาม = มีอาการอย่างหนึ่งในนี้  ( ไอ เจ็บคอ หอบเหนื่อยผิดปกติ มีน้ำมูก )
- ถ้ามีอาการอย่างใดอย่างหนึ่งให้ใส่ "1"

travel_risk_country: (string)
- คำถาม = มีประวัติเดินทางไปประเทศกลุ่มเสี่ยงในช่วง 14 วันก่อน .
- ให้ใช้ Country code ISO 3166-1 alpha-2 ความยาวสองตัวอักษรมาหนึ่งประเทศ
- Example: 'CN' for China, 'TH' for Thailand
For country code see the link below
https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2

covid19_contact: (string "0"/"1")
- คำถาม = อยู่ใกล้ชิดกับผู้ป่วยยืนยัน COVID-19 (ใกล้กว่า 1 เมตร นานเกิน 5 นาที) ในช่วง 14 วันก่อน  หรือ ไปสนามมวยลุมพินี  หรือ ผับที่มีการพบผู้ติดเชื้อ
- Example: "1" for yes

close_risk_country: (string "0"/"1")
- คำถาม = บุคคลในบ้านเดินทางไปประเทศกลุ่มเสี่ยง ในช่วง 14 วันก่อน
- Example: "1" for yes

int_contact: (string "0"/"1")
- คำถาม = ประกอบอาชีพใกล้ชิดกับชาวต่างชาติ
- Example "1" for yes

med_prof: (string "0"/"1")
- คำถาม = เป็นบุคลากรทางการแพทย์
- Example "1" for yes

close_con: (string "0"/"1")
- คำถาม = มีผู้ใกล้ชิดป่วยเป็นไข้หวัดพร้อมกัน มากกว่า 5 คน ในช่วง 14 วันก่อน
- Example "1" for yes


# Return (JSON)

gen_action (string)
- General recommendation e.g. wash your hand. 
(เป็นคำแนะนำกว้างๆ ในการปฏิบัติตัว)

spec_action (string)
- More specific recommendation on what you should do.
(คำแนะนำที่เฉพาะเจาะจงกับตัวเลือกมากขึ้น)

risk_level (string)
- 1-4 (4 is the highest risk level, 1 is the lowest)
ระดับความเสี่ยง 1 (ต่ำสุด) - 4 (สูงสุด)

# Database
Mongodb on Atlas cluster (Free tier)
For local deployment, please import the covid19_csv.csv in static\csv_for_mongodb

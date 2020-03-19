# Outbreak_api
Automatic risk stratification, and recommendation for Thailand COVID19

**This is a proof of concept product and subject to change before being deploy.**
**อยู่ระหว่างทดสอบขั้นต้นมากๆ อาจมีการปลี่ยนในอนาคต**

สำหรับแนวทางการจัดกลุ่มความเสี่ยงต้นฉบับ ดู XLSX file ใน static หรือ เข้าไปดูบน data.go.th  
https://data.go.th/dataset/covid19

## การใช้งาน
ยิง JSON ตามแนวทาน Input JSON (มีตัวอย่างด้านล่าง) ด้วย POST request มาที่ URL ใน link
[Pilot deployment on Heroku](https://flask-cds.herokuapp.com/covid19)

## Github link
[Outbreak API github](https://github.com/raynus/outbreak_api)


# To-do list
- Support non-Thai recommendation

# Input JSON, please submit to /covid19 route only

## JSON  ที่ส่งเข้ามา ต้องมี input ครบทุกตัว

**fever: (numeric/float)**
- คำถาม = มีไข้สูง 37.5 องศา (Celsius) ขึ้นไป หรือ รู้สึกว่ามีไข้ 
- ตัวเลขอุณหภูมิ ให้ใส่ตามจริง
- ในกรณีรู้สึกว่ามีไข้ ให้ใส่ตัวเลข 37.5 
- หากรู้สึกว่าไม่มีไข้หรือไม่ทราบอุณหภูมิ ใหใส่ 0
- Example : 37.55

**one_uri_symp: (string "0"/"1")**
- คำถาม = มีอาการอย่างหนึ่งในนี้  ( ไอ เจ็บคอ หอบเหนื่อยผิดปกติ มีน้ำมูก )
- ถ้ามีอาการอย่างใดอย่างหนึ่งให้ใส่ "1"

**travel_risk_country: (string)**
- คำถาม = มีประวัติเดินทางไปประเทศกลุ่มเสี่ยงในช่วง 14 วันก่อน
- ดูรายชื่อประเทศเสี่ยงด้วย route'/covid19/factors'
- ให้ใช้ Country code ISO 3166-1 alpha-2 ความยาวสองตัวอักษรมาหนึ่งประเทศ
- Example: 'CN' for China, 'TH' for Thailand
For country code see the link below
https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2

**covid19_contact: (string "0"/"1")**
- คำถาม = อยู่ใกล้ชิดกับผู้ป่วยยืนยัน COVID-19 (ใกล้กว่า 1 เมตร นานเกิน 5 นาที) ในช่วง 14 วันก่อน  หรือ ไปสนามมวยลุมพินี  หรือ ผับที่มีการพบผู้ติดเชื้อ
- Example: "1" for yes

**close_risk_country: (string "0"/"1")**
- คำถาม = บุคคลในบ้านเดินทางไปประเทศกลุ่มเสี่ยง ในช่วง 14 วันก่อน
- ดูรายชื่อประเทศเสี่ยงด้วย route'/covid19/factors' /
- Example: "1" for yes

**int_contact: (string "0"/"1")**
- คำถาม = ประกอบอาชีพใกล้ชิดกับชาวต่างชาติ
- Example "1" for yes

**med_prof: (string "0"/"1")**
- คำถาม = เป็นบุคลากรทางการแพทย์
- Example "1" for yes

**close_con: (string "0"/"1")**
- คำถาม = มีผู้ใกล้ชิดป่วยเป็นไข้หวัดพร้อมกัน มากกว่า 5 คน ในช่วง 14 วันก่อน
- Example "1" for yes


# Return (JSON)

**gen_action (string)**
- General recommendation e.g. wash your hand. 
(เป็นคำแนะนำกว้างๆ ในการปฏิบัติตัว)

**spec_action (string)**
- More specific recommendation on what you should do.
(คำแนะนำที่เฉพาะเจาะจงกับตัวเลือกมากขึ้น)

**risk_level (string)**
- 1-4 (4 is the highest risk level, 1 is the lowest)
ระดับความเสี่ยง 1 (ต่ำสุด) - 4 (สูงสุด)


# Example
## Input JSON to /covid19

{"fever":"37.55","one_uri_symp":"1","travel_risk_country":"SG","close_con":"1","covid19_contact":"0","close_risk_country":"0","int_contact":"0","int_contact":"0","med_prof":"0"}

## Return JSON
  {
    "gen_action": "ล้างมือ สวมหน้ากาก หลีกเลี่ยงที่แออัด",
    "risk_level": "4",
    "spec_action": "ให้ติดต่อสถานพยาบาลทันที"
  }


# Other route

## '/covid19/rules' 
Return all JSON rules from Mongodb
(ดึงฐานข้อมูล protocol ที่ใช้ในการจัดกลุ่ม และคำแนะนำทั้งหมด)

## '/covid19/factors'
Return all other risk factors and other configuration e.g. Fever temperature threshold and risk countries list   
(รหัสประเทศเสี่่ยง)
- Example
{
"RISK_COUNTRIES":['DE','CN','IT','KR','IR','FR','ES','US','CH','NO','JP','DK','NL','SE','UK'],
"FEVER_THRESHOLD":37.5
}


# Database
Mongodb on Atlas cluster (Free tier)
For local deployment, please import the covid19_csv.csv in static\csv_for_mongodb

from flask import Flask,render_template,request,jsonify
from flask_pymongo import PyMongo
from itertools import compress
from bson import json_util
#import pymongo
app=Flask(__name__)


#For local database
#app.config["MONGO_URI"]="mongodb://localhost:27017/Outbreak_casedef"

#For Mongodb Atlas
app.config["MONGO_URI"]="mongodb+srv://admin:admin@cluster0-esnsm.mongodb.net/Outbreak_casedef?retryWrites=true&w=majority"
mongo=PyMongo(app)

#Use ISO-2 code
ALLOWED_INPUT=['fever','one_uri_symp','travel_risk_country','covid19_contact','close_risk_country','int_contact','med_prof','close_con']

RISK_FACTORS={
"RISK_COUNTRIES":['DE','CN','IT','KR','IR','FR','ES','US','CH','NO','JP','DK','NL','SE','UK'],
"FEVER_THRESHOLD":37.5
}

ERR_DICT_KEY='missing_field'

def input_validation(input_d):
    #Remove irrevant item
    temp_dict={key:value for key, value in input_d.items() if key in ALLOWED_INPUT}
    not_in_allow=[not i in  temp_dict.keys() for i in ALLOWED_INPUT]

    if sum(not_in_allow) > 0:
        mis_input=" ".join(list(compress(ALLOWED_INPUT,not_in_allow)))
        temp_dict={ERR_DICT_KEY:mis_input}

    #replace dict with ERR_DICT_KEY to signal error

    return temp_dict


def check_other(input_d):
    #Check risk country
    if input_d['travel_risk_country'] in RISK_FACTORS["RISK_COUNTRIES"]:
        input_d['travel_risk_country']="1"
    else:
        input_d['travel_risk_country']="0"

    #Check fever
    if float(input_d['fever']) >RISK_FACTORS["FEVER_THRESHOLD"]:
        input_d['fever']="1"
    else:
        input_d['fever']="0"

    return input_d


@app.route('/')
def home_page():
    #Shows collection in Outbreak_casedef dbs
    case_def=mongo.db.COVID19.find_one_or_404({"dx":"COVID19"})


    return render_template('index.html')
@app.route('/covid19/factors',methods=['GET','POST'])
def show_factor():
    return jsonify(RISK_FACTORS)

@app.route('/covid19/rules',methods=['GET','POST'])
def dump_rules():
    rule=json_util.dumps(mongo.db.COVID19_action.find({}), indent=1, ensure_ascii=False).encode('utf8')
    return rule


@app.route('/covid19',methods=['GET','POST'])
def display():
    #For get, show API manual at this momemt


    if request.method=="POST":
        if request.is_json:
            input_json=request.get_json()
            input_json=input_validation(input_json)
            if ERR_DICT_KEY in input_json.keys():
                return input_json

            input_json=check_other(input_json)

            recommendation=list(mongo.db.COVID19_action.find(input_json,{'_id':0,'risk_level':1,'gen_action':1,'spec_action':1}))

            rec=[i for n, i in enumerate(recommendation) if i not in recommendation[n + 1:]]
            return jsonify(rec)

        else:
            rec="None JSON PPST"
            return rec

    else:


        #recommendation=list(mongo.db.COVID19_action.find(input,{'_id':0,'gen_action':1,'spec_action':1}))

        #https://stackoverflow.com/questions/9427163/remove-duplicate-dict-in-list-in-python
        #rec=[i for n, i in enumerate(recommendation) if i not in recommendation[n + 1:]]
        return render_template('output.html')

if __name__ == "__main__":
    app.run(debug = True,port=5000)

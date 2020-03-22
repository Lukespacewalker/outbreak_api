from flask import Flask,render_template,request,jsonify,make_response
from flask_pymongo import PyMongo
from itertools import compress
from bson import json_util
import pandas as pd
import requests
import json




app=Flask(__name__)


#For local database
#app.config["MONGO_URI"]="mongodb://localhost:27017/Outbreak_casedef"

#For Mongodb Atlas
app.config["MONGO_URI"]="mongodb+srv://admin:admin@cluster0-esnsm.mongodb.net/Outbreak_casedef?retryWrites=true&w=majority"
mongo=PyMongo(app)

db_obj=mongo.db.COVID19_action_test
meta_obj=mongo.db.metadata

RISK_FACTORS={
"RISK_COUNTRIES":['DE','CN','IT','KR','IR','FR','ES','US','CH','NO','JP','DK','NL','SE','UK'],
"FEVER_THRESHOLD":37.5
}

#Will replace the rest with string
VAR_TYPE_MAP={
    'numeric/float':1,
    'numeric':1,
    'float':1,
    'String':2
}

ERR_DICT_KEY='missing_field'



#The funcion update data type from mongo db
#use input from metadata sheet

#For mongodb var type see
#https://docs.mongodb.com/manual/reference/operator/aggregation/type/#available-types
# 1-Double
# 2-String
# 8-Boolean
# 16-Int

#Import is to string in defaut so the initiate type can be set to 2


# Will be spin out
def metadata_init():
    # Temporary use, will replace with data.go.th api


    METADATA=pd.json_normalize(meta_obj.find({}))
    METADATA.columns=map(str.lower,METADATA.columns)
    METADATA.columns=METADATA.columns.str.strip()
    METADATA['data_type_mapped']=METADATA['data_type'].map(VAR_TYPE_MAP).fillna(2)
    METADATA['mandatory_field_mapped']=METADATA['mandatory_field'].fillna(0)
    METADATA[["data_type_mapped", "mandatory_field_mapped"]] = METADATA[["data_type_mapped", "mandatory_field_mapped"]].apply(pd.to_numeric)
    return METADATA


METADATA=metadata_init()


#Use ISO-2 code
ALLOWED_INPUT=list(METADATA[METADATA['mandatory_field_mapped']>0]['attribute'])
#ALLOWED_INPUT=['fever','one_uri_symp','travel_risk_country','covid19_contact','close_risk_country','int_contact','med_prof','close_con']


#Update mongodb data type based on METADATA
# (Default import is string)



def input_validation(input_d):
    #Remove irrevant item
    temp_dict={key:value for key, value in input_d.items() if key in ALLOWED_INPUT}
    not_in_allow=[not i in  temp_dict.keys() for i in ALLOWED_INPUT]

    if sum(not_in_allow) > 0:
        mis_input=" ".join(list(compress(ALLOWED_INPUT,not_in_allow)))
        temp_dict={ERR_DICT_KEY:mis_input}

    #replace dict with ERR_DICT_KEY to signal error

    return temp_dict

#Helper function
#Input : data
#Output : numeric, coverted string to numeric or 0 if irrelvant character
#Convert all to double/numeric
def is_numeric(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def input_int(input):
    converted_input =0
    if is_numeric(input):
        converted_input=float(input)
    else:
        converted_input=input
    return converted_input



# Update require processing
# Support Fever of 0,1 and RISK_COUNTRIES of 0,1 for legacy
def check_other(input_d):
    #Check risk country

        #Check if old 0,1 were used
    if is_numeric(input_d['travel_risk_country']):
        temp_num=float(input_d['travel_risk_country'])
        if temp_num>0:
            input_d['travel_risk_country']=1
        else:
            input_d['travel_risk_country']=0
    else:
        if input_d['travel_risk_country'] in RISK_FACTORS["RISK_COUNTRIES"]:
            input_d['travel_risk_country']=1
        else:
            input_d['travel_risk_country']=0

    #Check fever

    if float(input_d['fever']) >=RISK_FACTORS["FEVER_THRESHOLD"]:
        input_d['fever']=1

    else:
        temp_fever=float(input_d['fever'])

        if temp_fever==float(1):
            input_d['fever']=1
        else:
            input_d['fever']=0

    #Get the rest done
    for i in ALLOWED_INPUT:
        if not i in ['fever','travel_risk_country']:
            input_d[i]=input_int(input_d[i])

    return input_d


@app.route('/')
def home_page():
    #Shows collection in Outbreak_casedef dbs
    case_def=mongo.db.COVID19.find_one_or_404({"dx":"COVID19"})


    return render_template('index.html')

@app.route('/covid19/factors',methods=['GET','POST'])
def show_factor():
    return jsonify(RISK_FACTORS)


#Dump all ruels to JSON file
@app.route('/covid19/rules',methods=['GET','POST'])
def dump_rules():
    rule=json_util.dumps(db_obj.find({}), indent=1, ensure_ascii=False).encode('utf8')
    return rule

#Show all servey question along with variable
@app.route('/covid19/questions',methods=['GET','POST'])
def show_question():
    questions=json_util.dumps(meta_obj.find({}), indent=1, ensure_ascii=False).encode('utf8')
    return questions

@app.route('/covid19',methods=['GET','POST'])
def display():
    #For get, show API manual at this momemt

    #db_type_update()
    if request.method=="POST":
        if request.is_json:
            input_json=request.get_json()
            input_json=input_validation(input_json)
            if ERR_DICT_KEY in input_json.keys():
                return input_json

            input_json=check_other(input_json)
            print(input_json)
            recommendation=list(db_obj.find(input_json,{'_id':0,'risk_level':1,'gen_action':1,'spec_action':1}))

            rec=[i for n, i in enumerate(recommendation) if i not in recommendation[n + 1:]]
            response = make_response(jsonify(rec), 200)
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Headers", "*")
            response.headers.add("Access-Control-Allow-Methods", "*")
            return response

        else:
            rec="None JSON POST"
            return rec

    else:
        #For GET

        #recommendation=list(mongo.db.COVID19_action.find(input,{'_id':0,'gen_action':1,'spec_action':1}))

        #https://stackoverflow.com/questions/9427163/remove-duplicate-dict-in-list-in-python
        #rec=[i for n, i in enumerate(recommendation) if i not in recommendation[n + 1:]]
        input_json_str=json.dumps(dict(request.args))
        input_json=json.loads(input_json_str)
        input_json=input_validation(input_json)
        if ERR_DICT_KEY in input_json.keys():
            return input_json

        input_json=check_other(input_json)

        recommendation=list(db_obj.find(input_json,{'_id':0,'risk_level':1,'gen_action':1,'spec_action':1}))

        rec=[i for n, i in enumerate(recommendation) if i not in recommendation[n + 1:]]
        return jsonify(rec)
        #return render_template('output.html')

if __name__ == "__main__":
    app.run(debug = False,port=5000)

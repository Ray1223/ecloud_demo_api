# app.py
from flask import Flask,jsonify,request,Response
import pymysql
import json
from config import db_config

app = Flask(__name__)

def get_db_conn(db_config):
    conn = pymysql.connect(host=db_config['host']
                           , port=db_config['port']
                           , database=db_config['database']
                           , user=db_config['user']
                           , password=db_config['password']
                           )
    return conn


def get_event(request):
    event = request.data.decode('utf8')
    event = json.loads(event)
    return event

@app.route('/billing/daily',methods=['POST'])
def billing_daily():

    event = get_event(request)

    if request.method == 'POST':
        if "lineitem/usageaccountid" in event:
            usageaccountid = event["lineitem/usageaccountid"]
        else:
            return Response(
                "There is no lineitem/usageaccountid parameter in body content",
                status=400,
            )


        conn = get_db_conn(db_config)
        cursor = conn.cursor()

        sql = """
        SELECT
            `product/ProductName`
            ,CONVERT(`lineItem/UsageStartDate`,DATE)
            ,ROUND(SUM(`lineitem/unblendedcost`),3)
        FROM billing
        WHERE `lineitem/usageaccountid`  = '{}'
        GROUP BY 
                 CONVERT(`lineItem/UsageStartDate`,DATE)
                ,`product/ProductName`
        ORDER BY 1,2
        """.format(usageaccountid)
        try:
            # Execute the SQL command
            cursor.execute(sql)
            last_item = ''
            final_dict = {}
            daily_dict = {}
            try:
                for row in cursor.fetchall():

                    item = row[0]
                    if last_item != item and last_item != '':
                        final_dict["{}".format(last_item)] = daily_dict
                        daily_dict = {}

                    daily_dict["{}".format(row[1])] = row[2]
                    last_item = row[0]
            except Exception as e:
                return Response(
                    "There is internal server error on request database",
                    status=500,
                )
            finally:
                final_dict["{}".format(last_item)] = daily_dict


            print(final_dict)
            # Commit your changes in the database
            conn.commit()
        except:
            # Rollback in case there is any error
            conn.rollback()

    return jsonify(final_dict)


@app.route('/billing/total',methods=['POST'])
def billing_total():

    event = get_event(request)

    if request.method == 'POST':
        if "lineitem/usageaccountid" in event:
            usageaccountid = event["lineitem/usageaccountid"]
        else:
            return Response(
                "There is no lineitem/usageaccountid parameter in body content",
                status=400,
            )


        conn = get_db_conn(db_config)
        cursor = conn.cursor()

        sql = """
        SELECT `product/ProductName`
               ,ROUND(SUM(`lineitem/unblendedcost`),3)
        FROM billing
        WHERE `lineitem/usageaccountid` = '{}'
        GROUP BY `product/ProductName`
        """.format(usageaccountid)

        try:
            # Execute the SQL command
            cursor.execute(sql)
            final_dict = {}
            for row in cursor.fetchall():
                final_dict["{}".format(row[0])] = row[1]
            # Commit your changes in the database
            conn.commit()
        except:
            # Rollback in case there is any error
            conn.rollback()
            return Response(
                "There is internal server error on request database",
                status=500,
            )
        finally:
            conn.close()
            cursor.close()

    return jsonify(final_dict)



# We only need this for local development.
if __name__ == '__main__':
 app.run()
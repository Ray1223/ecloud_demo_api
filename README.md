# eCloud Vally API Enhancement

### AWS Service duration:2021-08-30~2021-09-05

## how to use eCloud Vally API

Servers:`https://tsdczqspc3.execute-api.ap-northeast-1.amazonaws.com/dev`

1. lineItem/UnblendedCost grouping by product/productname
  
  	`POST` `/billing/total/`
   
   parameters:
   `{lineitem/usageaccountid: string}`

example:
```
POST https://tsdczqspc3.execute-api.ap-northeast-1.amazonaws.com/dev/billing/total
Content-Type: application/json
{
  "lineitem/usageaccountid": "959256351448"
}
```
```
{
  "AWS Data Transfer": 0.0,
  "AWS Lambda": 1.908,
  "Amazon DynamoDB": 0.0,
  "Amazon Simple Storage Service": 0.001,
  "Amazon Virtual Private Cloud": 72.0,
  "AmazonCloudWatch": 0.066
}

```

2. Get daily lineItem/UsageAmount grouping by product/productname

   `POST` `/billing/daily/`
   
   parameters:
   `{lineitem/usageaccountid: string}`

example:
```
POST https://tsdczqspc3.execute-api.ap-northeast-1.amazonaws.com/dev/billing/daily
Content-Type: application/json
{
  "lineitem/usageaccountid": "959256351448"
}
```
```
{
  "AWS Data Transfer": {
    "2020-04-01": 0.0
  },
  "AWS Lambda": {
    "2020-04-01": 0.008,
		..
  }
}

```
## eCloud Vally API architecture

[backend architecture photo](https://drive.google.com/file/d/1dW38-sR3TLFc_rf_-HtQls8OY4S227TJ/view?usp=sharing "backend architecutre")

主要使用flask架構建置API,並參考zappa serverless 部署在lambda上。

參考連結：[Deploy a Serverless Web App on AWS Lambda with Zappa](https://pythonforundergradengineers.com/deploy-serverless-web-app-aws-lambda-zappa.html "Deploy a Serverless Web App on AWS Lambda with Zappa")

## Database schema
### billing

| Column        | Schema  |  Null or not |
| --------   | ----- | :----:  |
|idx                                   | varchar(10)  | DEFAULT NULL
|bill/PayerAccountId          | varchar(20)  | DEFAULT NULL
|lineItem/UnblendedCost   | double         | DEFAULT NULL
|lineItem/UnblendedRate   | double         | DEFAULT NULL
|lineItem/UsageAccountId  | varchar(20)  | DEFAULT NULL
|lineItem/UsageAmount     | double         | DEFAULT NULL
|lineItem/UsageStartDate  | timestamp    | DEFAULT NULL
|lineItem/UsageEndDate    | timestamp    | DEFAULT NULL
|product/ProductName      | varchar(100) | DEFAULT NULL


### index
`lineitem/usageaccountid`,`product/ProductName`

### Future optimization direction
- add RDS proxy to use connection pool

## Billing Analysis
[billing insight](https://public.tableau.com/app/profile/ray.hsieh/viz/demo_report_16303192964010/ecloud_final_report?publish=yes "billing insight")

視覺化分析放在Tableau community,詳細的內容會再另外報告。



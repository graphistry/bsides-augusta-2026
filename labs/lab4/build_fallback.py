"""Build the offline fallback dataset for Lab 5.

Use this only when the lab backend (Splunk / Databricks via Louie) is down.

ATTACKER rows are reconstructed from the verified B2 evidence in
bots-bench/reports/botsv3_incidents/B2_aws_key_compromise/evidence (q1, q2, q4)
and the user-agent IOCs in IR_REPORT.md section 6.5: same IPs, keys, event names,
error codes, regions and user agents. RunInstances is subsampled (80 of 576).

BENIGN rows are SYNTHETIC. They use the real BOTSv3 IAM users (bstoll, btun,
frothly_admin, mkraeus, splunk_access) and the real benign activity the IR report
names (autoscaling RunInstances in us-west-1, bstoll's console ListUsers and
UpdateAccessKey), but source IPs come from documentation ranges (RFC 5737)
and the routine polling volume is invented.

Every row carries `provenance` so nobody mistakes this for raw BOTSv3.
Re-export a real pull with `events.to_csv(...)` from the notebook when the backend is up.
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(7)


def fake_sts():
    return "ASIA" + "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567") for _ in range(16))

OUT = Path(__file__).parent / "data" / "b2_cloudtrail_fallback.csv"
DAY = datetime(2018, 8, 20)

FIELDS = ["_time", "eventName", "eventSource", "awsRegion", "sourceIPAddress",
          "userIdentity.type", "userIdentity.userName", "userIdentity.accessKeyId",
          "userAgent", "errorCode", "provenance"]

UA_INITIAL = "Boto3/1.7.44 Python/2.7.12 Linux/4.4.0-1063-aws Botocore/1.10.44"
UA_MINER = "Boto3/1.7.42 Python/2.7.12 Linux/4.4.0-131-generic Botocore/1.10.42"
UA_ENUM = "Boto3/1.6.3 Python/2.7.14 Windows/2012ServerR2 Botocore/1.9.3"
UA_EWOLF = "ElasticWolf/5.1.6"
LEAKED_KEY = "AKIAJOGCDXJ5NW5PXUPA"
STS_KEY = "ASIAZB6TMXZ7LL6JBJQA"

SOURCES = {"CreateAccessKey": "iam", "CreateUser": "iam", "DeleteAccessKey": "iam",
           "ListAccessKeys": "iam", "GetUser": "iam", "ListUsers": "iam",
           "UpdateAccessKey": "iam", "GetCallerIdentity": "sts", "GetSessionToken": "sts",
           "ConsoleLogin": "signin", "ListBuckets": "s3", "GetBucketLocation": "s3",
           "GetMetricStatistics": "monitoring", "ListMetrics": "monitoring",
           "DescribeAlarms": "monitoring"}

REGIONS = ["us-east-1", "us-east-2", "us-west-1", "us-west-2", "ca-central-1", "eu-west-1",
           "eu-west-2", "eu-west-3", "eu-central-1", "ap-northeast-1", "ap-northeast-2",
           "ap-south-1", "ap-southeast-1", "ap-southeast-2", "sa-east-1"]


def ts(h, m, s):
    return (DAY + timedelta(hours=h, minutes=m, seconds=s)).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def row(t, name, ip, user, key, ua, err, region="us-west-1", itype="IAMUser", prov="reconstructed:attacker"):
    return {"_time": t, "eventName": name,
            "eventSource": SOURCES.get(name, "ec2") + ".amazonaws.com", "awsRegion": region,
            "sourceIPAddress": ip, "userIdentity.type": itype, "userIdentity.userName": user,
            "userIdentity.accessKeyId": key, "userAgent": ua, "errorCode": err, "provenance": prov}


rows = []

# --- Attacker: evidence q1 (leaked key AKIAJOGCDXJ5NW5PXUPA, 9 events) ---
for name, err in [("CreateAccessKey", "AccessDenied"), ("CreateUser", "AccessDenied"),
                  ("DeleteAccessKey", "AccessDenied"), ("GetCallerIdentity", "success"),
                  ("GetSessionToken", "success"), ("ListAccessKeys", "AccessDenied")]:
    rows.append(row(ts(9, 16, 12), name, "35.153.154.221", "web_admin", LEAKED_KEY, UA_INITIAL, err))
rows.append(row(ts(9, 16, 18), "ListAccessKeys", "209.107.196.112", "web_admin", LEAKED_KEY, UA_ENUM, "AccessDenied"))
rows.append(row(ts(9, 27, 6), "DescribeAccountAttributes", "82.102.18.111", "web_admin", LEAKED_KEY, UA_EWOLF,
                "Client.UnauthorizedOperation"))
rows.append(row(ts(9, 27, 7), "GetUser", "82.102.18.111", "web_admin", LEAKED_KEY, UA_EWOLF, "AccessDenied"))

# --- Attacker: evidence q4 (STS token, 139.198.18.205); one recon round per region ---
for i, region in enumerate(REGIONS):
    base = 14 + i * 2
    for j, (name, err) in enumerate([("GetCallerIdentity", "success"),
                                     ("CreateDefaultVpc", "Client.UnauthorizedOperation"),
                                     ("DescribeInstances", "Client.UnauthorizedOperation"),
                                     ("DescribeKeyPairs", "Client.UnauthorizedOperation")]):
        rows.append(row(ts(9, 16, base + j), name, "139.198.18.205", "web_admin", STS_KEY, UA_MINER, err, region=region))
rows.append(row(ts(9, 28, 54), "ListBuckets", "139.198.18.205", "web_admin", STS_KEY, UA_MINER, "AccessDenied"))

# --- Attacker: evidence q2, RunInstances subsample (80 of 576), mix of observed error codes ---
errs = (["Client.InstanceLimitExceeded"] * 39 + ["Client.UnauthorizedOperation"] * 26
        + ["Client.Unsupported"] * 14 + ["Server.InsufficientInstanceCapacity"] * 1)
for k, err in enumerate(errs):
    t = DAY + timedelta(hours=9, minutes=16, seconds=22) + timedelta(seconds=int(k * 300 / len(errs)))
    rows.append(row(t.strftime("%Y-%m-%dT%H:%M:%S.000Z"), "RunInstances", "139.198.18.205", "web_admin",
                    STS_KEY, UA_MINER, err, region=random.choice(REGIONS)))

# --- Benign (synthetic volume, real users / real benign activity types) ---
B = "synthetic:benign"
SPLUNK_UA = "Boto3/1.4.4 Python/2.7.12 Linux/4.4.0-1060-aws Botocore/1.5.82 Splunk-TA-AWS"
for _ in range(140):  # splunk_access polling, steady every ~20s
    t = DAY + timedelta(hours=9, seconds=random.randint(0, 45 * 60))
    name = random.choice(["DescribeInstances", "DescribeVolumes", "DescribeSecurityGroups", "DescribeSnapshots",
                          "ListBuckets", "GetBucketLocation", "GetMetricStatistics", "ListMetrics", "DescribeAlarms"])
    rows.append(row(t.strftime("%Y-%m-%dT%H:%M:%S.000Z"), name, "198.51.100.23", "splunk_access",
                    "AKIAIGKL572SFDPOKLHA", SPLUNK_UA, "success", region=random.choice(["us-west-1", "us-west-2"]), prov=B))

CONSOLE_UA = "signin.amazonaws.com"
for user, ip, n in [("frothly_admin", "203.0.113.40", 25), ("btun", "203.0.113.41", 20), ("mkraeus", "203.0.113.42", 20)]:
    rows.append(row(ts(9, random.randint(0, 10), random.randint(0, 59)), "ConsoleLogin", ip, user, "",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/68.0", "success", region="us-east-1", prov=B))
    for _ in range(n):
        t = DAY + timedelta(hours=9, seconds=random.randint(600, 45 * 60))
        name = random.choice(["DescribeInstances", "DescribeSecurityGroups", "ListBuckets", "GetBucketLocation",
                              "DescribeAlarms", "GetMetricStatistics"])
        rows.append(row(t.strftime("%Y-%m-%dT%H:%M:%S.000Z"), name, ip, user, fake_sts(), CONSOLE_UA,
                        "success", region="us-west-1", prov=B))

# Hard negatives: benign events that look like the attack
for k in range(6):  # real per evidence q2 note: 6 autoscaling RunInstances successes in us-west-1
    rows.append(row(ts(9, 5 + k * 6, 30), "RunInstances", "autoscaling.amazonaws.com", "", "",
                    "autoscaling.amazonaws.com", "success", region="us-west-1", itype="AWSService", prov=B + ":hard"))
for _ in range(8):  # a user without IAM rights poking around: AccessDenied but benign
    t = DAY + timedelta(hours=9, seconds=random.randint(0, 45 * 60))
    rows.append(row(t.strftime("%Y-%m-%dT%H:%M:%S.000Z"), random.choice(["ListUsers", "GetUser", "ListAccessKeys"]),
                    "203.0.113.42", "mkraeus", fake_sts(), CONSOLE_UA, "AccessDenied", prov=B + ":hard"))
# IR phase (real per b2_timeline_ir_phase.md): defenders, not attackers
bstoll_sts = fake_sts()
rows.append(row(ts(9, 35, 58), "ListUsers", "203.0.113.50", "bstoll", bstoll_sts, CONSOLE_UA, "success",
                prov=B + ":hard"))
rows.append(row(ts(9, 36, 12), "UpdateAccessKey", "203.0.113.50", "bstoll", bstoll_sts, CONSOLE_UA, "success",
                prov=B + ":hard"))

rows.sort(key=lambda r: r["_time"])
OUT.parent.mkdir(exist_ok=True)
with OUT.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows)
n_att = sum(r["provenance"].startswith("reconstructed") for r in rows)
print(f"wrote {OUT} rows={len(rows)} attacker={n_att} benign={len(rows) - n_att}")

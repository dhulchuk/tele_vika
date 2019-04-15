import datetime

import boto3
from boto3.dynamodb.conditions import Key

DYNAMODB = 'dynamodb'
REGION = 'eu-central-1'
TABLE = 'spent'


def get_db():
    return boto3.resource(
        DYNAMODB, region_name=REGION,
        # aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        # aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    )


def insert_spending(user_id: int, amount, tag):
    table = get_db().Table(TABLE)
    time_d = datetime.datetime.now()
    time = int(time_d.timestamp())
    table.put_item(Item={
        'UserId': user_id,
        'Amount': amount,
        'Tag': tag,
        'Timestamp': time,
    })


def get_spending(user_id: int, after: int = None):
    table = get_db().Table(TABLE)

    if after is None:
        now = datetime.datetime.now()
        after_d = now - datetime.timedelta(days=30)
        after = int(after_d.timestamp())

    res = table.query(KeyConditionExpression=Key('UserId').eq(user_id) & Key('Timestamp').gt(after))
    return res['Items']


if __name__ == '__main__':
    print(get_spending(123))

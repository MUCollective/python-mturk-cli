import sys
import boto3
import datetime
from tzlocal import get_localzone as tzlocal


# Use this boolean to control Production vs Sandbox mode (default to Sandbox).
production = False

# Use this string to differentiate batches of HIT assignments in order to run multiple batches concurrently.
batch = ''

# Use this boolean to control whether all HITs expire or just the last one to be created.
expire_all = False

# Read arguments for mode and expire.
script = sys.argv[0]
if (len(sys.argv) > 1):
    for i in range(len(sys.argv)):
        if (sys.argv[i] == '-prod'):
            # Create session in Production mode.
            production = True
        elif (sys.argv[i] == '-all'):
            # Set condition name.
            expire_all = True
        elif ((sys.argv[i] == '-batch') & (len(sys.argv) > (i + 1))):
            # Name .log files according to given batch name.
            batch = '-' + sys.argv[(i + 1)]

# Double check that we actually want to expire all HIts for this requester account.
if expire_all:
    ans = input("Are you sure want to expire all HIts for this requester account? (y/n)")
    if ans == 'n':
        sys.exit()
    else:
        print("You can extend HITs that were unintentially expired using update_expiration_for_hit(). https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mturk.html#MTurk.Client.update_expiration_for_hit")

# Designate target url for either Production or Sandbox.
if production:
    # Launch HIT on MTurk marketplace.
    endpoint = 'https://mturk-requester.us-east-1.amazonaws.com'
else:
    # Launch HIT on MTurk sandbox for testing.
    endpoint = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

# Connect to Requester account
session = boto3.Session(profile_name = 'default')
mturk = session.client('mturk',
   region_name='us-east-1',
   endpoint_url = endpoint
)

# Expire HIT(s)
if expire_all:
    # Get a list of all current HITs.
    hits = mturk.list_hits()
    print("*** Forcing " + str(len(hits['HITs'])) + " HITs to expire ***")

    # Iterate over HITs
    for hit in hits['HITs']:
        # Get HIT Id
        hit_id = hit['HITId']
        # Use HIT Id to force HIT to expire immediatedly
        mturk.update_expiration_for_hit(
            HITId = hit_id,
            ExpireAt = datetime.datetime(2015, 1, 1) # force HIT to expire by setting expiration date in the past
        )
else:
    # Get the information for the last HIT created from local file.
    last_hit ={}
    with open(file = 'logs/hit_info' + batch + '.log', mode = 'r') as hit_info:
        last_hit_string = hit_info.read()
        last_hit = eval(last_hit_string)
    print("*** Forcing HIT with Id " + last_hit['HITId'] + " to expire ***")
    # Get HIT Id
    hit_id = last_hit['HITId']
    # Use HIT Id to force HIT to expire immediatedly
    mturk.update_expiration_for_hit(
        HITId = hit_id,
        ExpireAt = datetime.datetime(2015, 1, 1) # force HIT to expire by setting expiration date in the past
    )
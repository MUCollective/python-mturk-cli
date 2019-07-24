import sys
import boto3
import datetime
from tzlocal import get_localzone as tzlocal


# Use this boolean to control Production vs Sandbox mode (default to Sandbox).
production = False

# Use this boolean to control whether all HITs expire or just the last one to be created.
delete_all = False

# Read arguments for mode and delete.
script = sys.argv[0]
if (len(sys.argv) > 1):
    for i in range(len(sys.argv)):
        if (sys.argv[i] == '-prod'):
            # Create session in Production mode.
            production = True
        elif (sys.argv[i] == '-all'):
            # Set condition name.
            delete_all = True

# Double check that we actually want to delete all HIts for this requester account.
if delete_all:
    ans = input("Deleted HITs can no longer be extended, approved, or rejected. Are you sure want to delete all HIts for this requester account? (y/n)")
    if ans == 'n':
        sys.exit()
    else:
        print("Clearing all HITs from Requester account.")

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

# Delete HIT(s)
if delete_all:
    # Get a list of all current HITs.
    hits = mturk.list_hits()
    print("*** Deleting " + str(len(hits['HITs'])) + " HITs ***")

    # Iterate over HITs
    for hit in hits['HITs']:
        # Get HIT Id
        hit_id = hit['HITId']
        # Use HIT Id to delete HIT.
        mturk.delete_hit(
            HITId = hit_id
        )
else:
    # Get the information for the last HIT created from local file.
    last_hit ={}
    with open('hit_info.log', 'r') as hit_info:
        last_hit_string = hit_info.read()
        last_hit = eval(last_hit_string)
    print("*** Deleting HIT with Id " + last_hit['HITId'] + " ***")
    # Get HIT Id
    hit_id = last_hit['HITId']
    # Use HIT Id to delete HIT.
    mturk.delete_hit(
        HITId = hit_id
    )
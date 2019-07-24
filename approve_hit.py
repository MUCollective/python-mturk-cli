import sys
import boto3
import datetime
from tzlocal import get_localzone as tzlocal


# Use this boolean to control Production vs Sandbox mode (default to Sandbox).
production = False

# Use this boolean to indicate if we are overriding a rejection.
override_reject = False

# Use this list to store workerIds of interest. 
# If we are overriding a previous rejection, only these workers will be approved.
# If we are NOT overriding a previous rejection (default), these workers will be skipped for approval.
worker_list = []

# Read arguments for mode, override, and workers.
script = sys.argv[0]
if (len(sys.argv) > 1):
    for i in range(len(sys.argv)):
        if (sys.argv[i] == '-prod'):
            # Create session in Production mode.
            production = True
        elif (sys.argv[i] == '-override'):
            # Override a previous rejection by approving this HIT.
            override_reject = True
        elif (i > 0):
            worker_list.append(sys.argv[i])

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

# Get the information for assignments in this HIT from local file.
assignments = []
with open('results.log', 'r') as results:
    results_string = results.read()
    assignments = eval(results_string)

# Exit if there is no assignment info.
if not assignments:
    print("No assignments in results.log. Try reruning get_results.py... terminating script")
    sys.exit()

# Iterate through assignments, approving them if they are not in the skip list.
for assignment in assignments:    
    # Determine whether or not and how to approve work depending on override_reject and worker_list arguments.
    if (not override_reject) and (not assignment['WorkerId'] in worker_list):
        # If we are not overrideing a previous reject, worker_list contains workers to skip.
        print("*** Approving work for worker: " + assignment['WorkerId'] + " ***")
        mturk.approve_assignment(
            AssignmentId = assignment['AssignmentId'],
            RequesterFeedback = 'Thank you for participating in our study.',
            OverrideRejection = False
        )
    elif override_reject and (assignment['WorkerId'] in worker_list):
        # If we are overrideing a previous reject, worker_list contains workers to approve.
        print("*** Overriding previous rejection for worker: " + assignment['WorkerId'] + " ***")
        mturk.approve_assignment(
            AssignmentId = assignment['AssignmentId'],
            RequesterFeedback = 'Thank you for participating in our study.',
            OverrideRejection = True
        )
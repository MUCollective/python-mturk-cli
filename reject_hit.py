import sys
import boto3
import datetime
from tzlocal import get_localzone as tzlocal


# Use this boolean to control Production vs Sandbox mode (default to Sandbox).
production = False

# Use this string to identify the batch of the HIT assignment.
batch = ''

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
        elif ((sys.argv[i] == '-batch') & (len(sys.argv) > (i + 1))):
            # Name .log files according to given batch name.
            batch = '-' + sys.argv[(i + 1)]
        elif (i > 0) and (sys.argv[i - 1] != '-batch'): 
            worker_list.append(sys.argv[i])

# Check that user has supplied at least one workerId
if not worker_list:
    print("Please provide at least one workerId as an argument... terminating script")
    sys.exit() 

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
with open(file = 'logs/results' + batch +'.log', mode = 'r') as results:
    results_string = results.read()
    assignments = eval(results_string)

# Exit if there is no assignment info.
if not assignments:
    print("No assignments in results" + batch + ".log. Try reruning get_results.py... terminating script")
    sys.exit()

# Iterate through assignments, approving them if they are not in the skip list.
for assignment in assignments:    
    # Reject work from workers in worker_list arguments.
    if (assignment['WorkerId'] in worker_list):
        # If we are overrideing a previous reject, worker_list contains workers to approve.
        print("*** Rejecting assignment from worker: " + assignment['WorkerId'] + " ***")
        mturk.reject_assignment(
            AssignmentId = assignment['AssignmentId'],
            RequesterFeedback = "You did not submit complete work for this assignment."
        )
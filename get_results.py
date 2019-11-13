import sys
import boto3
import datetime
from tzlocal import get_localzone as tzlocal


# Use this boolean to control Production vs Sandbox mode (default to Sandbox).
production = False

# Use this string to differentiate batches of HIT assignments in order to run multiple batches concurrently.
batch = ''

# Read argument for mode.
script = sys.argv[0]
if (len(sys.argv) > 1):
    for i in range(len(sys.argv)):
        if (sys.argv[i] == '-prod'):
            # Create session in Production mode.
            production = True
        elif ((sys.argv[i] == '-batch') & (len(sys.argv) > (i + 1))):
            # Name .log files according to given batch name.
            batch = '-' + sys.argv[(i + 1)]

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

# Get the information for the last HIT created from local file.
hit ={}
with open(file = 'logs/hit_info' + batch + '.log', mode = 'r') as hit_info:
    hit_string = hit_info.read()
    hit = eval(hit_string)
# Store HIT Id.
hit_id = hit['HITId']

# Update the information about this HIT.
hit = mturk.get_hit(
    HITId = hit_id
)

# Save HIT info to a .log file for subsequent access.
with open(file = 'logs/hit_info' + batch + '.log', mode = 'w') as hit_info:
    hit_info.write( str(hit['HIT']) )
print("*** Updating info for HIT with Id " + hit_id + " ***")

# Get information about the 'Submitted' Assignments for this HIT.
assignments = mturk.list_assignments_for_hit(
    HITId = hit_id
)

# Save Assignments information (results) to a .log file for subsequent access.
with open(file = 'logs/results' + batch + '.log', mode = 'w') as results:
    results.write( str(assignments['Assignments']) )
print("*** Writing information about completed assignments to logs/results" + batch + ".log ***")

# # Testing 
# with open(file = 'logs/results' + batch + '.log', mode = 'r') as results:
#     results_string = results.read()
#     assignments = eval(results_string)
#     print(len(assignments))
#     assignment_completed = len([assignment for assignment in assignments if assignment['AssignmentStatus'] == 'Submitted'])
#     print(assignment_completed)

# Count 'Submitted' assignements.
assignment_completed = len([assignment for assignment in assignments['Assignments'] if assignment['AssignmentStatus'] == 'Submitted'])

# Read out progress on HIT assignments.
print("Progress Report:")
print(str(assignment_completed) + "/" + str(hit['HIT']['MaxAssignments']) + " Assignments Completed")
print(str(hit['HIT']['NumberOfAssignmentsPending']) + "/" + str(hit['HIT']['MaxAssignments']) + " Assignments Pending")
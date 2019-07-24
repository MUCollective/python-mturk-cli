import sys
import boto3
from study_spec import spec, qualifications 


# Use this boolean to control Production vs Sandbox mode (default to Sandbox).
production = False

# Use this string to control the visualization condition. This will become a url parameter.
condition = ''

# Read arguments for launch mode and condition name.
script = sys.argv[0]
if (len(sys.argv) > 1):
    for i in range(len(sys.argv)):
        if (sys.argv[i] == '-prod'):
            # Launch in Production mode.
            production = True
        elif (i > 0):
            # Set condition name.
            condition = sys.argv[i]
            
# Make sure we have the condition name right.
while True:
    print("condition = " + condition)
    ans = input("Is this correct? (y/n)")
    if ans == 'y':
        break
    else:
        condition = input("What is the correct condition name? (Your response will be used as a url parameter)")

# Designate target urls for either Production or Sandbox.
if production:
    # Launch HIT on MTurk marketplace.
    endpoint = 'https://mturk-requester.us-east-1.amazonaws.com'
    preview = 'https://worker.mturk.com/mturk/preview?groupId='
else:
    # Launch HIT on MTurk sandbox for testing.
    endpoint = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
    preview = 'https://workersandbox.mturk.com/mturk/preview?groupId='

# Connect to Requester account
session = boto3.Session(profile_name = 'default')
mturk = session.client('mturk',
   region_name='us-east-1',
   endpoint_url = endpoint
)

# Read in XML Question file containing external HIT destination.
question = ''
with open(file = 'study.question', mode = 'r') as question_file:
    question = question_file.read()

# Add condition name after '0_landing?'
url_param = 'cond=' + condition # format condition as url parameter
idx = question.find('0_landing?') # find the place where the url parameter should be inserted
question = question[:idx + len('0_landing?')] + url_param + question[idx + len('0_landing?'):] # insert url parameter

# Create the HIT. Here we supply all the arguments we usually put in the .properties file for our external HIT.
hit = mturk.create_hit(
    Title = spec['title'],
    Description = spec['description'],
    Keywords = spec['keywords'],,
    Reward = spec['reward'],,
    MaxAssignments = spec['assignments'],,
    LifetimeInSeconds = spec['hit_lifetime'],,
    AssignmentDurationInSeconds = spec['assignment_duration'],,
    AutoApprovalDelayInSeconds = spec['auto_approval_delay'],
    Question = question,
    QualificationRequirements = qualifications
)
print("A new HIT has been created. You can preview it here:")
print(preview + hit['HIT']['HITGroupId'])

# Save HIT info to a .log file for subsequent access.
with open(file = 'hit_info.log', mode = 'w') as hit_info:
    hit_info.write( str(hit['HIT']) )
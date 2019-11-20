# Python Scripts for Running MTurk External HITs from the Command Line

This repo contains a lightweight API for running external HITs from the command line. The motivation behind this repo is to enable similar functionality to Amazon's old Command Line Interface (CLI) for MTurk, which [depreciated as of June 1st, 2019](https://forums.aws.amazon.com/ann.jspa?annID=6686). The scripts contained in this repo mostly mirror the core methods and workflow of the old MTurk CLI.

There are a couple files in this repo that must be configured to run a specific study. I will point out which scripts these are and how potential users can easily modify them to meet their needs.


---
## Set Up

These scripts use the `boto3` Python module. If you don't already have it installed, you can install it by running `pip install boto3` in the terminal.

You will also need to set up a file called `~/.aws/credentials`. This is where `boto3` will look for the security credentials for your MTurk Requester account. Storing these credentials locally mitigates security risks introduced when credentials are hardcoded into scripts like these. To create the credentials file, first navigate to the appropriate folder by entering `cd ~/.aws/` in the terminal, and then enter `touch credentials`. Use your preferred text editor to add the following to the credentials file.

```
[default]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET
```


---
## Contents and Documentation

Contents are split into General Purpose Scripts which should run without modification and Study-Specific Files which potential users should modify to meet their specific needs.

### General Purpose Scripts 

These scripts should work out of the box with no need to adjust them.

**approve_hit.py**

This script is used to approve work on assignments. The specific AssignmentIds that are approved are read in from the `logs/results*.log` file which is generated when you run `python get_results.py`. You can choose to skip over specific workers when approving a set of assignments for a HIT. Alternatively, you can choose to override previous rejections for a specific set of workers. Once approved, a HIT assignment cannot be subsequently rejected.

**Arguments:**

* *'-prod'* -- Approve HIT assignments run in the Production mode, rather than the Sandbox (default). If you do not supply this argument, assignments will only be approved if they were completed in the Sandbox.
* *'-override'* -- Approve HIT assignments for which work was previously rejected, overriding the rejection. If you supply this argument, you must also supply each WorkerId you want to approve.
* *'-batch'* -- If you are running multiple batches of HITs at once (e.g., for different conditions in an experiment), you must designate a name for each batch using the *'-batch'* argument followed by a unique identifier for each batch. For example, calling `python approve_hit.py -batch 1` would approve the assignements stored in the file `logs/results-1.log`. Note that the batch name follows the *'-batch'* argument separated by a space.
* *WorkerIds* -- You can supply a series of WorkerIds as arguments. If you are overriding a previous rejection, only these workers will be approved. If you are approving work for the first time, these workers will be skipped and their work will not be approved.

**Example:**

After launching a HIT in Production using `python create_hit.py -prod`, waiting for workers to finish their assignments, and generating a `logs/results.log` file using `python get_results.py -prod`, we can approve their work by running:

```
python approve_hit.py -prod
```


**create_hit.py**

This script creates a HIT according to the specifications in `study_spec.py` and `study.question`. It saves a file called `logs/hit_info*.log` which contains the HITId that is needed to access results, expire, or delete the HIT. In order to run multiple HITs from the same directory at once, use the *'-batch'* argument to prevent each new call to `python create_hit.py` from overwriting the `logs/hit_info.log` file.

**Arguments:**

* *'-prod'* -- Launch a HIT in Production mode, rather than the Sandbox (default). If you do not supply this argument, HITs will launch in the Sandbox.
* *'-batch'* -- If you are running multiple batches of HITs at once (e.g., for different conditions in an experiment), you must designate a name for each batch using the *'-batch'* argument followed by a unique identifier for each batch. For example, calling `python create_hit.py -batch 1` would create a new set of assignments for your HIT and store the HIT information in the file `logs/hit_info-1.log`. Note that the batch name follows the *'-batch'* argument separated by a space. This allows the user to launch multiple sets of HIT assignments concurrently as long as those sets of assignments have different batch names. 
* *'-cond'* -- If your external HIT relies on passing a condition name as a url parameter on the landing page (e.g., `https://external_hit_hostserver_url/landing_page?cond=<argument>`), you must supply a condition name as an argument using the *'-cond'* followed by the string representing the condition you would like to run. This is intended as a way to assign sets of workders to different versions of the task (e.g., in a between-subjects experiment). Omit the condition argument if you do not want to add a url parameter. 
**Note:** In order for condition assignment to work, you will need to open the code for `create_hit.py` and change the hardcoded variable `webpage_substring = 'landing_page?'` to match the substring at the end of the url for your external HIT. Be sure that your url ends in a '?' so that url parameters can be appended to create a well-formed web address.

**Example:**

We are running a study in Production mode, and we want to launch a HIT with a set of assignments in the 'control' condition. We should run:

```
python create_hit.py -prod -cond control
```


**delete_hit.py**

This script deletes a HIT based on the HITId stored in `logs/hit_info*.log`. Deleted HITs cannot be reviewed, so only do this once you finished accepting/rejecting work. You also have the option of deleting all HITs hosted by your requester account.

**Arguments:**

* *'-prod'* -- Delete a HIT that was launched in Production mode, rather than the Sandbox (default). If you do not supply this argument, HITs will be deleted only if they were run in the Sandbox.
* *'-all'* -- Delete all HITs hosted by your requester account. Be really careful about doing this, especially if you have multiple colleagues using the same requester account.
* *'-batch'* -- If you are running multiple batches of HITs at once (e.g., for different conditions in an experiment), you must designate a name for each batch using the *'-batch'* argument followed by a unique identifier for each batch. For example, calling `python delete_hit.py -batch 1` would delete the HIT whose HITId is stored in the file `logs/hit_info-1.log`. Note that the batch name follows the *'-batch'* argument separated by a space.

**Example:**

We are completely finished with a HIT we ran in Production mode, and we want clear it from our queue. We should run:

```
python delete_hit.py -prod
```


**expire_hit.py**

This script forces a HIT with its HITId stored in `logs/hit_info*.log` to expire immediately. Expiring a HIT is a new "stop button" if you lauched a HIT but realized that you made a mistake. This will prevent workers from accepting the remaining available HITs, but workers will still be able to finish pending HITs. You also have the option of expiring all HITs hosted by your requester account. Expired HITs can be extended using the `update_expiration_for_hit()` method in the `boto3` Python module, however, I have not yet created a script supporting this behavior.

**Arguments:**

* *'-prod'* -- Expire a HIT that was launched in Production mode, rather than the Sandbox (default). If you do not supply this argument, HITs will be expired only if they were run in the Sandbox.
* *'-all'* -- Expire all HITs hosted by your requester account. Be really careful about doing this, especially if you have multiple colleagues using the same requester account.
* *'-batch'* -- If you are running multiple batches of HITs at once (e.g., for different conditions in an experiment), you must designate a name for each batch using the *'-batch'* argument followed by a unique identifier for each batch. For example, calling `python expired_hit.py -batch 1` would expire the HIT whose HITId is stored in the file `logs/hit_info-1.log`. Note that the batch name follows the *'-batch'* argument separated by a space.

**Example:**

We launched a HIT in Production mode, but we want to stop workers from accepting any remaining available HITs. We should run:

```
python expire_hit.py -prod
```


**get_balance.py**

This script retrieves and reports the balance for your Requester account. Use this script to check how much money you have left to pay workers.

**Arguments:**

* *'-prod'* -- Retrieve balance for your Requester account (in Production mode), rather than the Sandbox (default). If you do not supply this argument, the balance reported will be $10,000 (in the Sandbox).

**Example:**

We want to know the balance for our Requester account. We should run:

```
python get_balance.py -prod
```


**get_results.py**

This script retrieves results for a HIT with its HITId stored in `logs/hit_info*.log`. Retrieving results entails three things: (1) Updating the `logs/hit_info*.log` file to reflect the current number of assignements available and pending; (2) Writing information about assignments with `Status == 'Submitted'` to a file called `logs/results*.log`; and (3) Writing a progress report on the current set of HIT assignments to the terminal, so the user can track how many assignements have been completed and how may are pending. The `logs/results*.log` file is required to run `python approve_hit.py`. Users should feel free to run this script repeatedly while waiting for workers to finish their assignments.

**Arguments:**

* *'-prod'* -- Retrieve results for a HIT that was launched in Production mode, rather than the Sandbox (default). If you do not supply this argument, results will be retrieved only if a HIT was run in the Sandbox.
* *'-batch'* -- If you are running multiple batches of HITs at once (e.g., for different conditions in an experiment), you must designate a name for each batch using the *'-batch'* argument followed by a unique identifier for each batch. For example, calling `python get_results.py -batch 1` would retrieve results for the HIT whose HITId is stored in the file `logs/hit_info-1.log`. Note that the batch name follows the *'-batch'* argument separated by a space. This allows the user to monitor progress on multiple sets of assignments concurrently as long as those sets of assignments have different batch names. 

**Example:**

We launched a HIT in Production mode, and we want to check the progress of workers. We should run:

```
python get_results.py -prod
```


**reject_hit.py**

This script is used to reject work on assignments. The specific AssignmentIds that are rejected are read in from the `logs/results*.log` file which is generated when you run `python get_results.py`. You must list the workerIds of workers whose assignments you wish to reject. 
Note that *it is unethical to reject HIT assignments in most cases*, as this amounts to a refusal to pay workers for completed assignements.

**Arguments:**

* *'-prod'* -- Reject HIT assignments run in the Production mode, rather than the Sandbox (default). If you do not supply this argument, assignments will only be rejected if they were completed in the Sandbox.
* *'-batch'* -- If you are running multiple batches of HITs at once (e.g., for different conditions in an experiment), you must designate a name for each batch using the *'-batch'* argument followed by a unique identifier for each batch. For example, calling `python reject_hit.py -batch 1 worker1234567` would reject the assignement stored in the file `logs/results-1.log` and submitted buy a worker with the workerId "worker1234567". Note that the batch name follows the *'-batch'* argument separated by a space.
* *WorkerIds* -- When calling this script, you must supply as arguments the WorkerIds of one or more workers whose work you wish to reject. Only these workers will be rejected.

**Example:**

After launching a HIT in Production using `python create_hit.py -prod`, waiting for workers to finish their assignments, and generating a `logs/results.log` file using `python get_results.py -prod`, we see that a user has submitted a fake completion token without actually logging any responses. We can reject this worker's assignement by running:

```
python reject_hit.py -prod worker1234567
```


### Study-Specific Files

These are the files you'll want to modify to run your own HITs.

**study_spec.py**

This script contains all the variable assignments that tell MTurk how to run your HIT. These are all the things that used to be specified in the .properties file for an external HIT when using the old command line interface (CLI). This file approximates the old study specification behavior using Python lists and dictionaries. 
We'll walk through the contents of the file I've provided in this repo to illustrate how you can modify it to set up your own HIT. First, the script `study_spec.py` defines a dictionary called `spec` containting information about the HIT title, description, reward, number of assignments, duration, etc.

```python
spec = {
    'title': 'Title of HIT',
    'description': 'This is the cursory description of the HIT that workers see before they choose to preview the HIT.',
    'keywords': 'keywords, separated, by, commas',
    'reward': '1.00',                # Reward is in dollars as a string.
    'assignments': 9,                # The number of assignments we want to run as an integer.
    'hit_lifetime': 259200,          # These last three variables are in seconds as integers.
    'assignment_duration': 2400,
    'auto_approval_delay': 604800
}
```

You'll want to change these values to set the behavior your want from the method [create_hit()](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/mturk.html#MTurk.Client.create_hit) from the `boto3` Python module, which is called when you run `python create_hit.py`.

Second, the script `study_spec.py` defines a list of dictionaries called `qualifications`. This is used to determine which workers are elegable to discover, preview, and accept the HIT.

```python
qualifications = [
    { # HIT approval rate > 97%
        'QualificationTypeId': '000000000000000000L0',
        'Comparator': 'GreaterThan',
        'IntegerValues': [97],
        'ActionsGuarded': 'DiscoverPreviewAndAccept' 
    }, { # Location in US
        'QualificationTypeId': '00000000000000000071',
        'Comparator': 'EqualTo',
        'LocaleValues': [{
            'Country': 'US' 
        }],
        'ActionsGuarded': 'DiscoverPreviewAndAccept' 
    }
]
```

You'll want to adjust the contents of `qualifications` to meet your needs. Find more information on how to specify MTurk qualifications requirements [here](https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_QualificationRequirementDataStructureArticle.html).


**study.question**

This file contains XML code that tells MTurk the url for your external HIT. To run your external HIT you will need to proved a link to your landing page in place of the dummy url in this file:

```
<ExternalURL>https://external_hit_hostserver_url/landing_page?</ExternalURL>
```

*If you intend to use `create_hit.py` to add a condition as a url parameter* (e.g., 'https://external_hit_hostserver_url/landing_page?*cond=control'): 

* Make sure you leave the '?' at the end of the external HIT url for your landing page so that url parameters can be appended to create a well-formed web address.
* You will need to open the code for `create_hit.py` and change the hardcoded variable `webpage_substring = 'landing_page?'` to match the substring at the end of the url for your external HIT. 


---
## Suggested Workflow

The following lists step through the most straightforward use cases for these scripts:

**Sandbox Testing:**

1. Set up your HIT by creating a website, adding the landing page url to `study.question`, and filling in `study_spec.py` to meet your needs.
2. Launch the HIT on the Sandbox for testing by running `python create_hit.py -cond <condition>`.
3. Get results from the Sandbox test run using `python get_results.py`. If you accidentally created extra HITs, you can force them to expire using `python expire_hit.py`.
4. Approve work using `python approve_hit.py`. 
5. Delete the HIT using `python delete_hit.py`.


**Running HITs in Production:**

1. Set up your HIT by creating a website, adding the landing page url to `study.question`, and filling in `study_spec.py` to meet your needs. *You should probably do Sandbox testing to check everything before launching in Production.*
2. Launch the HIT in Production mode by running `python create_hit.py -prod -cond <condition>`.
3. Get results from Production mode run using `python get_results.py -prod`. If you accidentally created extra HITs, you can force them to expire using `python expire_hit.py -prod`.
4. Approve work using `python approve_hit.py -prod`. 
5. Delete the HIT using `python delete_hit.py -prod`.


**Launching Multiple Batches of HIT Assignments Simultaniously:**

1. Set up your HIT by creating a website, adding the landing page url to `study.question`, and filling in `study_spec.py` to meet your needs. *You should probably do Sandbox testing to check everything before launching in Production.*
2. Launch multiple sets of HIT assignments simultaniously in Production mode by calling `create_hit.py` multiple times with different batch arguments. 

```
python create_hit.py -prod -cond condition1 -batch 1
python create_hit.py -prod -cond condition2 -batch 2
python create_hit.py -prod -cond condition3 -batch 3
```

3. Get results from each set of HIT assignments launched in Production mode using the same batch arguments.

```
python get_results.py -prod -batch 1
python get_results.py -prod -batch 2
python get_results.py -prod -batch 3
```

4. Approve work for each set of HIT assignments using the same batch arguments.

```
python approve_hit.py -prod -batch 1
python approve_hit.py -prod -batch 2
python approve_hit.py -prod -batch 3
```

5. Delete each HIT using the same batch argument. 
    
```
python delete_hit.py -prod -batch 1
python delete_hit.py -prod -batch 2
python delete_hit.py -prod -batch 3
```
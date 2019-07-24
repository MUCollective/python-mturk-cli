# Define the variables that describe the study to MTurk. 
# These are all the arguments we used to put in the .properties file for our external HIT under the old CLI.
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

# Define Qualifications for HIT as JSON. 
# Workers will not be able to even see the HIT if they do not meet these requirements.
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
    # }, { # Masters (Production Mode only, doesn't work on Sandbox)
        # 'QualificationTypeId': '2F1QJWKUDD8XADTFD2Q0G6UTO95ALH',
        # 'Comparator': 'Exists',
        # 'ActionsGuarded': 'DiscoverPreviewAndAccept' 
    }]
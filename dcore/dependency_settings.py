FRIENDLY_ERRORS = {
    'FIELD_ERRORS': {
        'CharField': {
            'password_incorrect': 2016,
            'password_mismatch': 2017,
            'not_editable': 2501,
            'invalid_token': 2502,
            'token_expired': 2503,
        },
        'ModelChoiceField': {
            'required': 2004,
            'null': 2024,
            'invalid_choice': 2081,
        },
    },
    'NON_FIELD_ERRORS': {
        'already_copied': 1501,
    }
}

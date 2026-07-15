ROLE_METADATA = {
    "finance": {
        "department": "Finance",
        "allowed_roles": ["Finance", "C-Level"],
        "security_level": "restricted",
        "owner": "Finance Team",
        "document_type": "Financial",
        "updated": "Quarterly"
    },

    "hr": {
        "department": "HR",
        "allowed_roles": ["HR", "C-Level"],
        "security_level": "restricted",
        "owner": "HR Team",
        "document_type": "HR",
        "updated": "Monthly"
    },

    "marketing": {
        "department": "Marketing",
        "allowed_roles": [
            "Marketing",
            "C-Level",
        ],
        "security_level": "restricted",
        "owner": "Marketing Team",
        "document_type": "Marketing",
        "updated": "Quarterly"
    },

    "engineering": {
        "department": "Engineering",
        "allowed_roles": ["Engineering", "C-Level"],
        "security_level": "restricted",
        "owner": "Engineering Team",
        "document_type": "Technical",
        "updated": "Quarterly"
    },

    "general": {
        "department": "General",
        "allowed_roles": [
            "Employee",
            "Finance",
            "HR",
            "Marketing",
            "Engineering",
            "C-Level"
        ],
        "security_level": "internal",
        "owner": "HR",
        "document_type": "Policy",
        "updated": "Yearly"
    }
}
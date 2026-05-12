package medviet.data_access

import future.keywords.if
import future.keywords.in

#################################
# DEFAULT DENY
#################################
default allow := false

#################################
# ADMIN OVERRIDE (highest privilege)
#################################
allow if {
    input.user.role == "admin"
}

#################################
# ML ENGINEER RULES
#################################
allow if {
    input.user.role == "ml_engineer"
    input.resource in {"training_data", "model_artifacts"}
    input.action in {"read", "write"}
}

# ML Engineer cannot delete production data
deny if {
    input.user.role == "ml_engineer"
    input.resource == "production_data"
    input.action == "delete"
}

#################################
# DATA ANALYST RULES
#################################
allow if {
    input.user.role == "data_analyst"
    input.resource == "aggregated_metrics"
    input.action == "read"
}

allow if {
    input.user.role == "data_analyst"
    input.resource == "reports"
    input.action == "write"
}

#################################
# INTERN RULES
#################################
allow if {
    input.user.role == "intern"
    input.resource == "sandbox_data"
    input.action in {"read", "write"}
}

#################################
# GLOBAL SECURITY RULE (HARD DENY)
#################################
deny if {
    input.data_classification == "restricted"
    input.destination_country != "VN"
    input.user.role != "admin"
}

#################################
# FINAL DECISION (important)
#################################
final_allow := allow if {
    not deny
}
"""Stand-ins for dbt cross-database macros, used ONLY by sqlfluff's jinja templater (linting).

dbt itself never uses this file: when dbt runs, the real macros write warehouse-specific SQL.
"""


def datediff(first_date, second_date, datepart):
    return f"datediff({datepart}, {first_date}, {second_date})"


def dateadd(datepart, interval, from_date_or_timestamp):
    return f"dateadd({datepart}, {interval}, {from_date_or_timestamp})"


def type_numeric():
    return "numeric(28, 6)"

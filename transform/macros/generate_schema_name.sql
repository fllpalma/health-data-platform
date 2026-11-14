{#-
  Use the layer's schema name as-is ("staging", "intermediate", "marts")
  instead of dbt's default "analytics_staging". Common company convention.
-#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {{ custom_schema_name | trim if custom_schema_name is not none else target.schema }}
{%- endmacro %}

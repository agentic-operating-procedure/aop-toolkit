# RB-LINE-001: Line Fault Management Procedure

## Objective

Restore the affected service for a reported line fault within the maintenance window, minimising customer impact.

## Outcome

The reported fault is correlated, diagnosed and either resolved or dispatched to a field crew, with the resolution recorded against the fault ticket.

## In scope

- Line faults reported on the monitored network segment
- Faults triaged by the shift operations desk

## Out of scope

- Customer premise equipment faults
- Planned maintenance windows

## Steps

- correlate-alarms
- loopback-test
- resolve-fault
- dispatch-field-crew
- notify-planning

## Decision rules

- if mttr_estimate > 120 then escalate to shift supervisor [approval-required]
- if customer_tier == 'priority' and outage == true then request human approval before dispatch [approval-required]
- if loopback_failures >= 3 then engage on-call engineer [prohibited]

## Exceptions

- three failed loopbacks -> escalate to on-call-engineer

## Escalation

Severe faults are escalated to the shift supervisor.

# Shared Data Generator

This folder contains the shared synthetic data generator for the Singpass anti-fraud portfolio.

It is responsible for generating the common backend tables used by both projects:

- `users`
- `devices`
- `user_devices`
- `services`
- `sessions`
- `events`
- `fraud_labels`

## Structure

- `config/`: generation settings and scenario ratios
- `src/`: generator code

## Initial goal

The first implementation target is a small synthetic dataset that matches the shared backend schema and can be inspected quickly.

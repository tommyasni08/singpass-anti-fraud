# Initial Research on Singpass

Last updated: 8 April 2026

## Purpose of this document

This document is a short research note prepared before starting any Singpass-related anti-fraud project.

It serves two purposes:

1. To build a basic understanding of Singpass so that I do not work on fraud problems that are irrelevant to the product and its operating model.
2. To show that the project directions taken later are supported by an initial research attempt rather than generic anti-fraud assumptions.

## What Singpass is

Singpass is Singapore's national digital identity system. It acts as a trusted identity layer used across government services and selected private-sector services.

At a high level, Singpass is more than a login tool. It supports:

- secure authentication
- consent-based data sharing
- identity verification
- digital signing and transaction authorisation

This matters because fraud risk in Singpass is not limited to account access alone. Abuse can happen when Singpass is used as a trusted gateway into downstream financial, identity, telecom, or service-enablement actions.

## Core components relevant to anti-fraud

### 1. Authentication / Login

Singpass supports secure login across digital services. Official Singpass materials show that the Singpass app plays a central role in authentication.

Common user-facing methods include:

- Singpass app login using fingerprint, face recognition, or a 6-digit passcode
- QR login, where a user scans a QR code and approves the login through the Singpass app
- selected verification flows such as Face Verification in some contexts

For anti-fraud purposes, this means Singpass should not be treated as a typical username-password consumer account system. The main risk is not only whether credentials are correct, but whether the approval or login action is genuinely intended by the rightful user.

### 2. Myinfo

Myinfo is Singpass' verified data-sharing layer. It allows users to share verified personal data with government agencies and participating private-sector organisations after authentication and consent.

This reduces the need for manual data entry and improves trust in the underlying identity data.

From an anti-fraud perspective, this changes the problem shape:

- the issue is less about fake self-declared profile data
- the issue is more about whether the correct user knowingly consented to the requested data sharing

### 3. Digital Signing

Sign with Singpass allows users to digitally sign documents and approve high-trust transactions through the Singpass ecosystem.

Official documentation describes this as a cryptographically backed signing flow tied to the user's digital identity. This makes it materially different from lightweight e-signature experiences used in lower-trust consumer flows.

For anti-fraud work, this is important because misuse of signing or approval can have higher consequence than ordinary login abuse.

### 4. Access Scope

Singpass is used across both public and private sector services.

Examples include:

- public-sector services such as IRAS, ICA, CPF-related services, and other government transactions
- private-sector services such as banking, insurance, and telecommunications use cases

This broad scope means that suspicious identity events can have downstream consequences across multiple service domains.

## Concrete Singpass abuse patterns identified

A later review of recent Singapore Police Force materials made the initial research more concrete.

The most useful refinement is that Singpass should be treated not only as a login system, but as a trusted enabler that can be misused for downstream fraud.

Three abuse patterns stand out as especially relevant:

### 1. Fraudulent account creation in downstream financial services

A compromised or relinquished Singpass account can be used to create downstream financial accounts that later support scam activity.

This is important because the loss does not need to happen inside Singpass itself. The damage happens when a trusted identity event is used to open or enable accounts elsewhere.

### 2. Sale or relinquishment of Singpass accounts or credentials

Singpass abuse does not always begin with technical compromise. In some cases, account holders may sell, surrender, or recklessly hand over their Singpass credentials to third parties.

This creates a very different fraud problem from ordinary account takeover. In this case, the attacker may gain near-complete control over the trusted identity layer and then use it for downstream abuse.

### 3. Stolen or deceptively obtained Singpass credentials

Some abuse does not involve full voluntary relinquishment. Instead, the victim may be deceived into giving access, approving flows, or allowing data sharing without properly understanding the consequences.

This is especially relevant to scam-led approval abuse, malicious consent journeys, and cases where the user is tricked into enabling a fraudulent action that appears technically valid.

## Why these three abuse patterns matter

These three patterns give a more defensible anti-fraud framing for the portfolio than a broad list of hypothetical harms.

They imply three different control problems:

- preventing suspicious live access into the Singpass account
- detecting cases where the attacker already has near-full control of the Singpass account
- identifying deceptive or malicious use of trusted approvals, consent, or downstream identity actions

They also help clarify why Singpass abuse can still be high impact even though Singpass is not itself a stored-value wallet or bank account.

The harm comes from what trusted identity access enables afterwards.

## Security and trust model: high-level understanding

Based on the official materials reviewed, Singpass is built around a high-trust identity and authentication model that includes:

- multi-factor authentication
- app-based approval and verification
- explicit user consent for selected data-sharing flows
- strong identity binding to real individuals
- secure token-based/API-based integration patterns

The Singpass app functions as a major trust anchor in the user journey. This is significant for fraud analysis because risk shifts away from weak, low-assurance identity patterns and toward abuse of trusted user approvals or high-trust digital actions.

## Why Singpass is different from a normal consumer account system

The most important takeaway from this research is that Singpass should be treated as a high-signal identity system.

In this context, high-signal means:

- accounts are tied to real, previously verified individuals
- identity data is drawn from authoritative sources
- there is less identity noise than on ordinary internet platforms

This changes the anti-fraud problem in several ways.

Compared with general consumer apps, Singpass is less centered on:

- fake account creation
- synthetic identity abuse
- low-cost mass account farming

Instead, a larger share of the risk is likely to sit in:

- sale or relinquishment of Singpass credentials
- stolen or compromised Singpass credentials
- social engineering and malicious approvals
- scam-led consent abuse
- device compromise or remote-control scenarios
- suspicious post-authentication activity
- misuse of trusted identity access for downstream fraud

## Key anti-fraud implication

For Singpass, the question is often not only `is this the real user?`

It is also:

`is the real user knowingly and safely approving this action?`

That distinction is important.

A user may successfully authenticate, yet the overall event may still be fraudulent in intent if the user was manipulated, coached, deceived, or pressured into approving a harmful action.

This makes Singpass especially relevant for anti-fraud work focused on:

- intent inference
- anomaly detection
- approval-risk assessment
- post-login or post-approval monitoring
- downstream misuse prevention

## What this research means for project relevance

The purpose of this research is not to claim full expertise on Singpass. It is to ensure that any project built around Singpass anti-fraud starts from the right problem frame.

Based on this initial review, a Singpass-relevant anti-fraud project should avoid overfocusing on generic fraud patterns such as fake-account creation or simple credential stuffing alone.

A more relevant project direction would focus on:

- suspicious live login or approval events
- sale, surrender, or compromise of Singpass credentials
- risk in app-based or QR-based authentication journeys
- anomalous behaviour after successful authentication
- early detection of misuse after a trusted identity event
- downstream abuse enabled by trusted identity access

These areas appear more aligned with how fraud risk would realistically concentrate in a system like Singpass.

## Conclusion

This research suggests that Singpass is best understood as a trusted national digital identity system rather than a standard login product.

Because identity quality is relatively strong, the anti-fraud challenge is less about verifying whether an account belongs to a real person, and more about detecting when a trusted identity, trusted approval, or trusted Singpass account is being abused.

This initial understanding is important because it helps keep future project work relevant to Singpass instead of drifting into generic fraud problems that fit other products better than they fit a national digital identity system.

The strongest abuse patterns identified for this portfolio are:

- fraudulent account creation in downstream financial services
- sale or relinquishment of Singpass accounts or credentials
- stolen or deceptively obtained Singpass credentials used for malicious approvals or unconsented data sharing

## Sources consulted

These sources were reviewed on 8 April 2026.

- GovTech Singpass overview: https://www.tech.gov.sg/products-and-services/singpass/
- GovTech Singpass API for businesses: https://www.tech.gov.sg/products-and-services/for-businesses/corporate-transactions/singpass-api
- Singpass app overview: https://app.singpass.gov.sg/
- Singpass Login documentation: https://docs.developer.singpass.gov.sg/docs/products/singpass-login
- Singpass Login FAQ: https://docs.developer.singpass.gov.sg/docs/products/singpass-login/faq
- Myinfo technical documentation: https://docs.developer.singpass.gov.sg/docs/legacy-myinfo-v3-v4/technical-specifications/myinfo-v4
- Sign with Singpass overview: https://docs.sign.singpass.gov.sg/
- Sign with Singpass user flow: https://docs.sign.singpass.gov.sg/for-users/how-to-sign
- SPF Annual Scam and Cybercrime Brief 2025: https://www.police.gov.sg/-/media/SPF/Media-Room/Statistics/Annual-Scams-and-Cybercrime-Brief-2025/Annual-Scam-and-Cybercrime-Brief-2025.pdf
- SPF news release on relinquished Singpass credentials, 17 July 2025: https://www.police.gov.sg/media-room/news/20250717_15_persons_investigated_for_their_suspected_involvement
- SPF news release on unauthorised address changes using stolen or compromised Singpass accounts, 14 January 2025: https://www.police.gov.sg/Media-Room/News/20250114_seven_persons_arrested_in_relation_to_the_series_of_unauthorised_attempts

# Agentic Commerce Protocol (ACP) + AP2 + Agent Payments — Full Production Guide 2026
## The Transaction Layer: How Agents Discover, Authorize, Pay, and Fulfill — ACP (OpenAI+Stripe) + AP2 (Google+FIDO) + x402 + UCP + MCP + A2A + Visa TAP + Mastercard Agent Pay

> **Core Thesis 2026:** We solved how agents get context (MCP), how they talk to each other (A2A), how they store knowledge (OKF). Now we solve how they **move money**. 2026 is the year infrastructure standards are being locked in. Agentic commerce = AI agent acts as buyer holding delegated authority to discover products, authorize spending within set limits, execute payments on user's behalf. Agent receives goal in natural language ("order trail-running shoes under $150 that arrive Friday"), plans steps, queries merchants, evaluates options against constraints, authorizes payment within preset limits, triggers fulfillment. Unlike recommendation engine or chat assistant, agent transacts: it moves money and produces order at end of conversation. McKinsey projects $3-5T global retail spend orchestrated by agents by 2030, up to $1T US B2C alone. Juniper April 2026 forecast puts agentic commerce spend $1.5T in 2030; total agentic transaction value $8B in 2026. Adobe Analytics measured 4,700% YoY jump generative-AI traffic to US retail sites July 2024-July 2025. Coinbase-led x402 payment protocol processed ~165M agent transactions first months. Agentic traffic converts 15-30% — 5-10x improvement over traditional e-commerce benchmarks Q1 2026 data. But only ~12 Shopify merchants went live before OpenAI retired Instant Checkout March 2026 — protocol fragmentation is real. 6 protocols define working stack as of April 2026: ACP, UCP, AP2, MCP, A2A, Visa TAP — most production deployments compose 2-3 together. ACP is checkout handshake, AP2 is authorization layer proving human authorized, x402 is settlement rail. MCP moves context does not create it. This guide covers 7-layer stack, 6 protocols, 4-step lifecycle, Shared Payment Tokens, cryptographic mandates, production code Node.js+Postgres+Stripe.

### Table of Contents
1. What is Agentic Commerce? Definition, 3 Forms, Market Size
2. The 4-Step Lifecycle — Discovery → Authorization → Payment → Fulfillment
3. The 7-Layer Agentic Commerce Stack
4. The 6 Protocols Powering Agentic Commerce (April 2026)
5. Deep Dive: ACP — Agentic Commerce Protocol (OpenAI + Stripe)
6. Deep Dive: AP2 — Agent Payments Protocol (Google → FIDO Alliance)
7. Deep Dive: x402, MPP, UCP, Visa TAP, Mastercard Agent Pay
8. ACP vs UCP vs AP2 vs x402 vs MPP — Comparison Table
9. Production Architecture — How MCP + A2A + ACP + AP2 Compose
10. Shared Payment Token + Mandates — How Money Moves Without Exposing Cards
11. Node.js Production Implementation — MCP Server + A2A + ACP Checkout
12. Database Schema — Postgres + pgvector + ClickHouse for Agent Commerce
13. Security, Trust, Fraud — Mandates, Signed Agent Cards, TAP
14. Failure Modes & What Went Wrong — Why Instant Checkout Retired
15. Future — $3-5T by 2030, Stablecoins Default for M2M

---

### 1. What is Agentic Commerce? Definition, 3 Forms, Market Size

**Definition:** Agentic commerce is category of online purchasing where AI agent acts as buyer operating with delegated authority. Agent receives goal in natural language, plans steps required to satisfy it, queries merchants or marketplaces, evaluates options against user's constraints, authorizes payment within preset limits, triggers fulfillment. Unlike recommendation engine or chat assistant, agent transacts: it moves money and produces order at end conversation.

Agentic commerce is model in which autonomous AI agents act as proxies for buyers executing full purchase lifecycle (discovery, authorization, payment, fulfillment) from goal rather than click. Instead of person browsing site and pressing buy, agent reads instruction like "order trail-running shoes under $150 that arrive Friday," evaluates options across merchants, completes transaction inside wallet, chat surface, or checkout protocol.

**3 working forms 2026:**

- **Consumer-side agents:** OpenAI's ChatGPT with Instant Checkout, Perplexity's Comet browser, Amazon's Rufus, Google AI Mode shopping initiate purchases on behalf individual user
- **Enterprise-side agents:** Microsoft Copilot, Salesforce Agentforce, custom internal agents reorder office supplies, renew SaaS subscriptions, pay invoices on behalf company
- **Machine-to-machine agents:** Pay micro-amounts for API calls, compute, data feeds using protocols designed for sub-cent transactions — x402, MPP

**Market sizing:**

- McKinsey QuantumBlack Oct 2025 study projects agentic commerce will orchestrate $3T-$5T global retail spend by 2030 with up to $1T US B2C alone
- Juniper April 2026 forecast tighter view putting agentic commerce spend $1.5T in 2030; June 2026 study puts total agentic transaction value $8B in 2026
- Adobe Analytics measured 4,700% YoY jump generative-AI traffic to US retail sites between July 2024-July 2025
- Coinbase-led x402 processed roughly 165M agent transactions in first months
- Agentic traffic converts at 15-30% — 5-10x improvement over traditional e-commerce benchmarks per Q1 2026 data
- Global agentic commerce volume by 2030 McKinsey: 2026 year infrastructure standards being locked in — decisive happened during 2024 holiday shopping season, at NRF 2026 consensus clear: agentic commerce moved from experiment to commercial infrastructure

### 2. The 4-Step Lifecycle — Discovery → Authorization → Payment → Fulfillment

Every agent purchase moves through four steps. Discovery first, then authorization, then payment, then fulfillment. Each step has different set protocols and different set failure modes. Only works when each step composes with next.

**Step 1: Discovery — agent learns what merchants exist, what products they sell, what payment methods they accept.**

Two protocols dominate:

- **MCP (Anthropic, open-sourced Nov 2024, donated AAIF Dec 2025):** Agent query any compliant server for tools and data over JSON-RPC 2.0 — search catalog, query inventory DB, read return policy
- **UCP (Google, announced NRF 2026 Jan):** Exposes merchant capability profiles so agent can list supported services (checkout, product search, returns) before it transacts

Shopping agent that runs MCP for discovery still needs ACP or UCP for checkout call.

**Step 2: Authorization — agent proves to merchant that real user delegated purchase, merchant proves to network agent legitimate.**

Layer where most agent-fraud risk concentrates and most contested protocol layer.

- **AP2 (Google, introduced Sept 16 2025, v0.2 April 28 2026, donated to FIDO Alliance April 2026):** Introduces cryptographic mandates — signed digital receipts where user attests to specific transaction intent — tamper-evident, cryptographically signed credentials recording what user approved
- **Visa TAP (Trusted Agent Protocol, launched Oct 14 2025 with Cloudflare):** Signs agent's identity into HTTP request headers; merchants verify signature against Visa's directory
- **Mastercard Agent Pay (Announced April 29 2025):** Uses tokenized payment credentials for agent-led purchases — enrollment, identity verification, authentication of consumer intent and checkout with tokenized payload

AP2 authorizes. Doesn't move money and doesn't place orders.

**Step 3: Payment — agent moves funds.**

For card rails dominant pattern scoped ephemeral credential:

- **ACP (OpenAI + Stripe, launched Sept 29 2025, Apache 2.0, spec stable April 17 2026):** Shared Payment Token (SPT) bound to specific merchant and specific dollar amount, time-bounded, single-use. Buyer’s payment provider issues token scoped to specific merchant and specific amount with short expiry. Agent passes token to merchant; merchant runs it through its normal processor (typically Stripe)
- **Mastercard Agentic Tokens (part of Agent Pay):** Similarly operate
- **For onchain rails:** Agents pay in stablecoins over Coinbase x402 or Stripe MPP

**Step 4: Fulfillment — merchant runs order through existing pipeline (warehouse, logistics, customer service).**

Agentic commerce does not replace fulfillment infrastructure; sits in front of it. Merchant retains relationship with buyer for refunds and dispute handling plus post-purchase support even when agent placed order on buyer's behalf.

**Conceptual Purchase Flow: Permission → Request → Settlement:**

Permission (AP2 mandate) → Payment Request (ACP SPT or x402 402) → Settlement (Stripe, Visa, Base onchain). Mandate or voucher does not necessarily mean funds have reached seller — need verification responsibilities defined.

### 3. The 7-Layer Agentic Commerce Stack

Rye checkout-execution startup published 7-layer framework that has become most-cited reference taxonomy for category. Each layer maps to different set incumbents and different cluster well-funded startups.

**Layer 1: AI platforms and agent surfaces — where shopping journeys originate**

Named platforms OpenAI (ChatGPT), Google (AI Mode, Gemini), Anthropic (Claude), Perplexity (Comet browser), Amazon (Rufus), Microsoft (Copilot), Meta. Each surface decides which merchants its agents can transact with and which protocols it supports.

**Layer 2: Protocols and standards — communication layer**

ACP (OpenAI + Stripe), UCP (Google + Shopify), AP2 (Google + payment networks), MCP (Anthropic/Linux Foundation AAIF Dec 2025), A2A (Google), Visa TAP all sit here. Adoption open question: most merchants need support more than one.

**Layer 3: Payments and identity — financial rails**

Network incumbents Visa, Mastercard, PayPal and processors Stripe, Adyen, Checkout.com compete with well-funded startup tier. Basis Theory raised $33M Series B Oct 2025 led Costanoa, Skyfire raised $9.5M from Neuberger Berman a16z CSX Coinbase Ventures, Nekuda raised $5M seed May 2025 Madrona with Amex Ventures Visa Ventures participating. Combined total across just three ~$47.5M concentrated entirely on agent-payment infrastructure.

**Layer 4: Card issuance — programmable virtual cards agent can spin up per merchant or per session**

Lithic, Stripe Issuing, Marqeta, Highnote, Ramp, Brex are named players. Bridge between agentic protocols and existing card-network universe.

**Layer 5: Checkout execution — browser robot layer**

When merchant has not adopted ACP or UCP agent still needs way complete purchase. Rye, Induced AI, Henry Labs and other vendors run automation that fills out checkout forms on merchant's actual site. Rye itself raised $14M.

**Layer 6: Merchant enablement and discovery — product-data and catalog layer**

Shopify, commercetools, BigCommerce, Adobe, SAP supply e-commerce backends; specialists Salsify, Syndigo, Akeneo standardize product feeds that agents read.

**Layer 7: Trust and security — fraud, bot detection, agent verification**

HUMAN Security, Riskified, Forter, Signifyd, Kasada, DataDome, Akamai, Cloudflare sit here. Agentic Commerce Consortium formed by Basis Theory with Lithic, Crossmint, Skyfire, Rye, Channel3 and others publishing security standards across this layer.

**Insignia Business Review April 2026 analysis argues durable value will accrue to settlement rails (stablecoin issuers, payment facilitators) rather than open-source protocols themselves — same logic TCP/IP captured no rents while Akamai, Cloudflare, AWS captured plenty. Thesis contested but informs strategic acquirers positioning.**

### 4. The 6 Protocols Powering Agentic Commerce (April 2026)

Six protocols define working stack as of April 2026: ACP, UCP, AP2, MCP, A2A, Visa TAP. Most production deployments compose two or three together. Each handles different slice discovery, authorization, payment, or trust layer.

| Protocol | Backer | Scope | Status | Layer |
|---|---|---|---|---|
| ACP Agentic Commerce Protocol | OpenAI + Stripe, PayPal as payment provider, co-developed Stripe OpenAI Meta spec April 2026 | Checkout conversation between agent and merchant — checkout sessions, cart and product feed, delegated payment, delegated authentication, orders, webhooks | Used ChatGPT Instant Checkout Sept 29 2025-March 2026; ACP spec remains, open-source Apache 2.0, still labeled beta, April 2026 release added carts, product feed API and MCP binding | Transaction |
| UCP Universal Commerce Protocol | Google + 20+ retailers Shopify Walmart Target Best Buy Etsy PayPal Visa Stripe Amex co-developed | Discovery, checkout, post-purchase across journey — product discovery and capability negotiation plus checkout and post-purchase handoff | Announced NRF 2026 Jan keynote Sundar Pichai; available now; spec Aug 25 2026 stable | Discovery+Transaction |
| AP2 Agent Payments Protocol | Google + 60+ orgs Coinbase Mastercard PayPal Revolut Salesforce Worldpay Adyen Amex; donated to FIDO Alliance April 2026, now at FIDO; started at Google Sept 16 2025; partners Mastercard American etc | User-consent mandates for agent-initiated payments — proof user authorized — authorization layer | Production-ready; PayPal partnership live; v0.2 April 28 2026 separates Checkout Mandate from Payment Mandate; defines verification responsibilities; payment processing belongs to processor not new settlement network | Authorization & Trust |
| MCP Model Context Protocol | Anthropic open-sourced Nov 2024 donated AAIF Dec 2025 co-founded Block OpenAI | Agent-to-tool data plane — discover and call tools search catalog query inventory DB read return policy | Open-sourced Nov 2024 borrows transport ideas Language Server Protocol runs JSON-RPC 2.0; Google Microsoft OpenAI Visa Mastercard all committed within 6 months; MCP now upstream every commerce protocol | Discovery |
| A2A Agent-to-Agent | Google | Agent-to-agent task delegation — shopping agent delegates price comparison specialist or checkout to merchant-side agent | Production at 150+ orgs April 2026 Insignia Microsoft Azure AI Foundry Amazon Bedrock AgentCore Salesforce | Agent Coordination |
| Visa TAP Trusted Agent Protocol | Visa + Cloudflare | Cryptographic agent identity for merchant-side trust — signs agent identity into HTTP request headers merchants verify signature against Visa directory | Launched Oct 14 2025 | Trust & Security |

Plus additional rails:

- **x402 (Coinbase, launched May 6 2025, V2 Dec 11 2025):** Carries payment exchange — server quotes payment requirements client signs payment retries request facilitator can verify and settle. Does not prescribe single payment rail. V2 distinguishes schemes typically settle immediately from batch settlement which authorizes payment upfront and redeems value onchain later. Handles how money moves inside web request — stablecoin default settlement currency for M2M. Foundation operational July 14 2026. 165M agent transactions first months
- **MPP Machine Payments Protocol (Stripe + Tempo, March 18 2026, co-authors):** Settlement sessions and streaming — stablecoins on Tempo cards via Stripe and Visa Bitcoin via Lightning — metered recurring streaming agent workloads — agent's wallet must hold supported method — metered per-call billing for APIs stablecoin and fiat (cards Klarna Affirm) via Shared Payment Tokens
- **Mastercard Agent Pay + Agent Pay for Machines:** Card-based program uses tokenized payment credentials — enrollment identity verification authentication consumer intent checkout tokenized payload — integrators must register with Mastercard issuer authorizes transaction — connects agents to card payments rather than replacing card network with new cryptocurrency. Agent Pay for Machines introduced June 10 2026 combines credentialing programmatically enforced spending rules with settlement across cards accounts stablecoins — opened early access Oct 20 offering initial buyer and seller side APIs toolkit sandbox docs — builds on x402 agent answers 402 Payment Required response with signed voucher within approved limit seller verifies delivers service vouchers can be combined redeemed later — still in pilot not available commercially

### 5. Deep Dive: ACP — Agentic Commerce Protocol (OpenAI + Stripe)

**What:** Open standard from OpenAI and Stripe for connecting buyer's agent to merchant, checkout handshake. Protocol that powers ChatGPT Instant Checkout. Built jointly by OpenAI and Stripe to make existing online checkouts navigable by AI agent instead of human filling out form. Lets business define how agent can complete purchase using merchant's own existing commerce and payment stack — no separate agent-only checkout to build.

**Core primitive: Shared Payment Token (SPT):** Instead of exposing buyer's saved card to agent, buyer's payment provider issues token scoped to specific merchant and specific amount with short expiry. Agent passes token to merchant; merchant runs it through normal processor (typically Stripe). OpenAI launched ACP Sept 29 2025 with Etsy first integrated merchant; live with real merchants including Etsy Coach Kate Spade Urban Outfitters brands as of 2026. See Stripe announcement full.

**Spec:** Open-source Apache 2.0, labeled beta, spec stable April 17 2026. Created by Stripe OpenAI Meta current spec April 2026: checkout sessions, cart and product feed, delegated payment, delegated authentication, orders, webhooks.

**Cost:** Processes payment via Stripe's standard merchant acquiring infrastructure. Charges 4% OpenAI platform fee + about 3% Stripe processing fee = 7% total for autonomous agent-led conversions per Payscale Magazine analysis.

**Timeline and pivot:**

- Sept 29 2025: OpenAI launched ACP with Etsy first merchant; Shopify integration announced but onboarding stalled
- March 2026: OpenAI said first version Instant Checkout not flexible enough and moved ChatGPT focus to product discovery with merchants using own checkout. Only about dozen Shopify merchants went live before OpenAI retired Instant Checkout March 2026 in favor dedicated retailer apps (Walmart Target Instacart) inside ChatGPT
- April 2026 release added carts, product feed API and MCP binding
- March 24 2026: OpenAI announced expanding ACP to product discovery letting merchants use own checkout experiences merchants now use ACP to share product feeds promotions with ChatGPT
- As of Oct 2026: ACP now routes most buyers back to merchant — keeps checkout upsells analytics intact — narrowed role since March 2026 OpenAI stopped completing purchases inside ChatGPT now routes buyers to merchant own checkout

**Flow (original Instant Checkout → current discovery-first):**

Original:

1. User in ChatGPT: "Order trail-running shoes under $150 arrive Friday"
2. Agent queries merchants via product feed API
3. Agent presents options, user selects
4. Agent creates checkout session via ACP
5. Payment provider issues SPT scoped merchant+amount+expiry
6. Agent passes SPT to merchant
7. Merchant runs SPT through Stripe processor like normal card
8. Merchant fulfills order, sends order confirmation + webhooks

Current discovery-first (post March 2026):

1. AI handles product research and intent (discovery)
2. Merchants retain control checkout under ACP
3. Buyer routed to merchant site with cart pre-filled via ACP
4. Merchant's existing checkout handles payment (conversion lives at merchant)

**Why merchants care:** Where conversion lives. ACP now routes most buyers back to you which keeps checkout upsells analytics intact vs UCP similar. OpenAI pivoted from Instant Checkout only ~12 active merchants out of millions to visual product discovery with checkout on retailer site — agentic traffic converts 15-30% 5-10x improvement traditional benchmarks but need own checkout control.

**ACP checkout session example (pseudo):**

```json
{
  "checkout_session": {
    "id": "cs_acp_123",
    "merchant_id": "etsy_456",
    "cart": {
      "items": [
        {"sku": "trail-shoe-123", "qty": 1, "price": 12900}
      ],
      "total": 12900,
      "currency": "USD"
    },
    "shared_payment_token": {
      "token": "spt_xxx_merchant_scoped",
      "merchant_id": "etsy_456",
      "amount": 12900,
      "currency": "USD",
      "expires_at": "2026-10-29T23:59:59Z",
      "single_use": true
    },
    "delegated_authentication": {
      "user_id": "user_789",
      "auth_method": "oauth"
    },
    "status": "pending"
  }
}
```

Merchant runs token:

```javascript
const paymentIntent = await stripe.paymentIntents.create({
  amount: 12900,
  currency: "usd",
  payment_method_data: {
    type: "shared_payment_token",
    shared_payment_token: { token: "spt_xxx" }
  }
});
```

### 6. Deep Dive: AP2 — Agent Payments Protocol (Google → FIDO Alliance)

**What:** Open payment-agnostic protocol from Google focuses on trust and authorization. Authorization and trust — proves that human authorized spend and that agent is legitimate — proving user or organization actually authorized agent to make purchase. Payment-consent layer: person authorizes agent once within set limits and token proves consent without exposing banking data. Payment-agnostic framework for users merchants payments providers to transact with confidence across all types payment methods. Built to work with Google's Agent2Agent (A2A) protocol and Model Context Protocol (MCP) so it can slot into agent frameworks without replacing them.

**Does not move money — hands off to rail.** Google's own extension wires it to x402 for stablecoin payments. Establishes payment-agnostic framework — also supports different payment types — from credit and debit cards to stablecoins and real-time bank transfers. Authorizes doesn't move money and doesn't place orders. Partners include Mastercard American Express etc.

**Timeline:**

- Sept 16 2025: Google introduced AP2 as open protocol that can run as extension A2A and MCP built with more than 60 organizations including Coinbase Mastercard PayPal Revolut — announcement says supports cards real-time bank transfers stablecoins
- Oct 2025: Visa TAP launch complementary
- April 28 2026: v0.2 released — separates Checkout Mandate (proof what agent may buy) from Payment Mandate authorizing payment for that checkout. For autonomous purchases user-signed open mandates set constraints and agent signs finalized mandates within them. Defines verification responsibilities; payment processing belongs to payment processor not new AP2 settlement network
- April 2026: Donated to FIDO Alliance, released v0.2 which adds human not present purchases — Cygnux reports Google donated AP2 to FIDO Alliance April 2026 and released v0.2
- March 5 2026: Mastercard and Google co-developed Verifiable Intent announced as authorization-record standard aligned with AP2 — sample implementation link
- Google publishes AP2 sample using x402-compatible payments

**3 Mandates (Fireblocks summary as 3 cryptographically signed mandates carried as verifiable credentials):**

1. **Intent Mandate:** What user asked for — spend within scope like "under $50 on office supplies" — user-signed open mandate sets constraints
2. **Cart Mandate:** What agent assembled — approve these exact items — proof what agent may buy — finalized mandate agent signs within open mandate constraints
3. **Payment Mandate:** What gets charged — signals to payment network that agent was involved — authorizing payment for that checkout

Each authorization is cryptographic mandate signed by user (typically by user's wallet or AP2-compatible identity provider). Agent presents mandate at checkout. Mandate carries merchant identifier plus transaction amount and expiry. Merchant verifies signature runs payment stores mandate as non-repudiable receipt. AP2 was developed with PayPal and other payment partners; protocol UCP defaults to for payment step.

**v0.2 spec separation:**

- **Checkout Mandate:** Proof of what agent may buy
- **Payment Mandate:** Authorizing payment for that checkout
- For autonomous purchases user-signed open mandates set constraints agent signs finalized mandates within them
- Verification responsibilities defined

**AP2 flow:**

1. User authorizes agent once: "You can spend up to $150 on trail shoes this week" → User signs Intent Mandate (open mandate with constraints merchant, amount, expiry, category)
2. Agent discovers product trail-shoe $129 Etsy
3. Agent creates Cart Mandate: exact items sku qty price merchant
4. Agent signs finalized mandates within open mandate constraints
5. Agent presents mandates + payment token at checkout
6. Merchant verifies signature against AP2 identity provider / FIDO directory
7. Payment processor verifies Payment Mandate
8. Settlement via chosen rail (card, bank transfer, stablecoin via x402)
9. Merchant stores mandate as non-repudiable receipt for disputes

**AP2 mandate example (pseudo):**

```json
{
  "intent_mandate": {
    "id": "intent_123",
    "user_id": "user_789",
    "constraints": {
      "max_amount": 15000,
      "currency": "USD",
      "category": "footwear",
      "merchants": ["etsy", "nike", "adidas"],
      "expires_at": "2026-11-05T00:00:00Z"
    },
    "signature": "user_signed_jwt_xxx",
    "issuer": "fido_ap2_wallet"
  },
  "cart_mandate": {
    "id": "cart_456",
    "intent_id": "intent_123",
    "merchant_id": "etsy_456",
    "items": [{"sku": "trail-shoe-123", "price": 12900}],
    "total": 12900,
    "agent_id": "shopping-agent-v1",
    "signature": "agent_signed_within_intent_yyy",
    "verifiable": true
  },
  "payment_mandate": {
    "id": "pay_789",
    "cart_id": "cart_456",
    "amount": 12900,
    "rail": "card",
    "payment_method": "shared_payment_token",
    "agent_involved_flag": true,
    "signature": "payment_signed_zzz"
  }
}
```

**Payment-agnostic:** Can work with cards, bank rails, stablecoins. Google's extension wires to x402 for stablecoin payments. Partners Mastercard Amex Adyen Coinbase PayPal Revolut Salesforce Worldpay.

**Human Not Present (HNP):** v0.2 adds human not present purchases — autonomous buying within pre-authorized limits without user actively present at checkout — critical for enterprise reorder agents and M2M.

### 7. Deep Dive: x402, MPP, UCP, Visa TAP, Mastercard Agent Pay

**x402 (Coinbase, May 6 2025, V2 Dec 11 2025, Foundation operational July 14 2026):**

- Carries payment exchange — how money moves inside web request
- In documented HTTP flow server quotes payment requirements client signs payment retries request facilitator can verify and settle it
- Does not prescribe single payment rail — current V2 distinguishes schemes typically settle immediately from batch settlement which authorizes payment upfront and redeems value onchain later
- Stablecoins default settlement currency for M2M — well-funded startup tier
- Foundation operational July 14 2026 contributed to open governance
- Processed ~165M agent transactions first months per Eco guide
- Flow: Server returns 402 Payment Required with payment requirements → Client signs payment → Retries request with signed payment → Facilitator verifies and settles → Seller delivers service; vouchers can be combined redeemed later

**MPP Machine Payments Protocol (Stripe + Tempo, March 18 2026):**

- Settlement sessions and streaming — stablecoins on Tempo cards via Stripe and Visa Bitcoin via Lightning — metered recurring streaming agent workloads — agent's wallet must hold supported method
- Metered per-call billing for APIs stablecoin and fiat (cards Klarna Affirm) via Shared Payment Tokens
- Ideal use cases: Agent-to-business purchases at scale, API calls, compute, data feeds sub-cent transactions
- Stripe and Tempo co-authors

**UCP Universal Commerce Protocol (Google, announced NRF 2026 Jan, Sundar Pichai keynote, spec Aug 25 2026):**

- Google's answer to ACP designed to span full journey rather than checkout call — open-source protocol announced Jan 2026
- Backers Shopify Walmart Target Best Buy Etsy PayPal Visa Stripe Amex — co-developed with Shopify Walmart Target others
- Composes with AP2 for payments and MCP for tool access which is part why Google positions it as universal rather than competitor to ACP
- Technical scope covers product discovery and capability negotiation plus checkout and post-purchase handoff — discovery checkout post-purchase across journey
- Available now, composes with AP2 payments and MCP tool access

**Visa TAP Trusted Agent Protocol (Visa + Cloudflare, launched Oct 14 2025):**

- Cryptographic agent identity for merchant-side trust
- Signs agent's identity into HTTP request headers merchants verify signature against Visa's directory
- Introduced with Cloudflare — enrollment identity verification authentication consumer intent
- Authorization-record standard aligned with AP2 — Mastercard and Google co-developed Verifiable Intent announced March 5 2026 as authorization-record standard aligned with AP2

**Mastercard Agent Pay + Agent Pay for Machines:**

- Card-based program uses tokenized payment credentials for agent-led purchases — enrollment identity verification authentication consumer intent checkout tokenized payload — integrators must register with Mastercard issuer authorizes transaction — connects agents to card payments rather than replacing card network with new cryptocurrency
- Agent Pay for Machines introduced June 10 2026 combines credentialing programmatically enforced spending rules with settlement across cards accounts stablecoins — opened early access Oct 20 offering initial buyer seller side APIs toolkit sandbox docs — builds on x402 agent answers 402 Payment Required response with signed voucher within approved limit seller verifies delivers service vouchers can be combined redeemed later — still in pilot not available commercially
- Concrete example per Oct 20 account: marketing agency Hype approved one budget for agent that bought research from AIsa and eight images through Cloudflare AI Gateway — nine payments to two merchants — Coinbase Developer Platform supplied wallet infrastructure Base supplied onchain settlement network BVNK handled fiat or stablecoin payment and settlement

**Additional protocols summary table:**

| Protocol | Backer | Launched | Scope | Payments | Status |
|---|---|---|---|---|---|
| ACP | OpenAI + Stripe PayPal | Sept 2025 | Commerce checkout conversation physical digital goods | Fiat through merchant's existing payment provider conversational checkout | Live Etsy Coach etc 12 Shopify merchants retired Instant Checkout March 2026 still spec April 17 2026 stable |
| UCP | Google Shopify Walmart Target | Jan 2026 | Discovery checkout post-purchase across journey | AP2 + multiple rails | Announced NRF 2026 available spec Aug 25 2026 |
| AP2 | Google FIDO Alliance 60+ orgs | Sept 2025 v0.2 April 2026 | User-consent mandates agent-initiated payments authorization layer proof user authorized on any rail | Payment-agnostic cards bank stablecoins | Production PayPal live donated FIDO April 2026 human not present |
| x402 | Coinbase | May 6 2025 V2 Dec 11 2025 | Settlement pay-per-request stablecoin settlement how money moves inside web request | Stablecoins onchain immediate vs batch | 165M txns foundation July 14 2026 |
| MPP | Stripe Tempo | March 18 2026 | Settlement sessions streaming metered recurring | Stablecoins Tempo cards Stripe Visa Bitcoin Lightning metered per-call billing | Live |
| MCP | Anthropic Linux Foundation AAIF | Nov 2024 | Agent-to-tool data plane | N/A | Open-sourced donated Dec 2025 upstream every commerce protocol |
| A2A | Google | April 2025 | Agent-to-agent delegation | N/A | Production 150+ orgs Azure Bedrock Salesforce |
| Visa TAP | Visa Cloudflare | Oct 14 2025 | Cryptographic agent identity | N/A | Launched |
| Mastercard Agent Pay | Mastercard | April 29 2025 / Machines June 10 2026 | Card-based tokenized credentials programmatically enforced spending rules | Cards accounts stablecoins | Pilot not commercially |

### 8. ACP vs UCP vs AP2 vs x402 vs MPP — Comparison Table

| Dimension | ACP (Agentic Commerce Protocol) | UCP (Universal Commerce Protocol) | AP2 (Agent Payments Protocol) | x402 | MPP (Machine Payments) |
|---|---|---|---|---|---|
| Backers | OpenAI + Stripe PayPal as payment provider | Google co-developed Shopify Walmart Target etc | Google donated FIDO 60+ Coinbase Mastercard PayPal Revolut Salesforce Worldpay | Coinbase | Stripe Tempo co-authors |
| Launched | Sept 2025 | Jan 2026 | Sept 2025 v0.2 April 2026 | May 2025 V2 Dec 2025 | March 18 2026 |
| Latest spec | 2026-04-17 stable | 2026-08-25 | 2026-04-28 v0.2 | 2026-12-11 V2 foundation July 14 2026 | March 2026 |
| Scope | Checkout conversation agent-merchant — checkout sessions cart product feed delegated payment delegated auth orders webhooks | Discovery checkout post-purchase across journey | User-consent mandates agent-initiated payments — authorization layer — proves user authorized what agent buys on any rail | Pay-per-request stablecoin settlement — how money moves inside web request | Settlement sessions streaming metered recurring streaming agent workloads |
| Payments | Delegated tokens Stripe Shared Payment Token PayPal — fiat through merchant existing provider | AP2 + multiple rails | Payment-agnostic framework — cards debit stablecoins real-time bank transfers — establishes framework users merchants payments providers transact confidence — does not move money hands off to rail — extension wires to x402 stablecoin | Stablecoins onchain — server quotes payment requirements client signs retries facilitator verifies settles — schemes immediate vs batch | Stablecoins on Tempo cards via Stripe Visa Bitcoin Lightning — metered per-call billing APIs stablecoin fiat cards Klarna Affirm via Shared Payment Tokens |
| Where conversion lives | Now routes most buyers back to merchant keeps checkout upsells analytics intact — original Instant Checkout inside ChatGPT retired March 2026 after ~12 merchants | Merchant site but discovery via Google AI Mode | Authorization only — merchant retains relationship | Merchant existing fulfillment | Merchant existing |
| Cost | 4% OpenAI platform fee + ~3% Stripe = 7% total autonomous agent-led conversions | Varies | Rail-agnostic — processing via chosen processor | Stablecoin fees low sub-cent | Metered |
| Ideal use cases | Conversational checkout physical digital goods inside ChatGPT — agent-ready checkout lets business define how agent can complete purchase using merchant own existing commerce payment stack no separate agent-only checkout build — live Etsy Coach Kate Spade Urban Outfitters | Full journey discovery to post-purchase — 20+ retailers | Consumer purchases through AI assistants Human Not Present autonomous buying within pre-authorized limits — enterprise reorder — M2M | M2M micro-payments API calls compute data feeds — digital service purchases — 165M txns first months | Agent-to-business purchases scale API calls compute |
| Open source | Apache 2.0 | Open source | Open payment-agnostic | Open | Open |
| Interop | Composes with AP2 payments MCP tool access | Composes with AP2 MCP | Works with A2A MCP UCP — extension x402 — verification responsibilities defined — payment processing belongs to processor not new AP2 settlement network | Works with AP2 mandates — verification — facilitator verifies settles | Shared Payment Tokens |

**Which should e-commerce brand prioritize?** Summary UCP and ACP for discovery checkout — ACP now discovery-first product research intent merchants retain control checkout under ACP — UCP full journey. AP2 for authorization proof. x402/MPP for settlement micro-payments. Most merchants will need support more than one — protocols designed to compose but composition still being negotiated real time.

### 9. Production Architecture — How MCP + A2A + ACP + AP2 Compose

**2026 production equation extended with commerce:**

```
(Cross-Cloud Lakehouse × Knowledge Catalog) + MCP Server + (A2A Swarm @ TPU v8i) + (Agent Gateway + Model Armor) + Vertex AI Memory Bank + (ACP Checkout + AP2 Mandates + x402 Settlement) = Production-Ready Agentic Commerce OS
```

**Layered architecture for agentic commerce — actually ships:**

User Goal: "Order trail-running shoes under $150 that arrive Friday"

↓

**Layer 1 — Discovery (MCP + UCP + OKF):**

Supervisor Agent (A2A orchestrator) → Retriever Agent via A2A Task: retrieve

- MCP tools: product_search (File Search Tool replaces RAG, OKF bundle for product catalog), inventory_check, policy_check (refunds policy page 25), store_hours
- UCP: merchant capability profiles list supported services checkout product search returns
- OKF: knowledge bundle concepts/shoes.md policies/shipping.md tables/inventory.md path=ID links=graph portable Git-reviewable

↓

**Layer 2 — Authorization (AP2 + Visa TAP + Signed Agent Cards):**

Executor Agent → AP2 wallet

- User previously authorized Intent Mandate: "You can spend up to $150 on footwear this week" — user-signed JWT
- Agent creates Cart Mandate exact items sku qty price merchant
- Signs finalized mandates within open mandate constraints
- Agent Card at /.well-known/agent-card.json now includes payment_methods + authentication schemes Bearer OAuth2 — v1.0 signed Agent Cards for crypto identity verification enterprise multi-tenancy
- Visa TAP signs agent identity into HTTP headers merchant verifies against Visa directory

↓

**Layer 3 — Payment (ACP SPT + x402/MPP rail):**

- ACP: Agent creates checkout session cart total 12900 → Payment provider issues Shared Payment Token scoped merchant+amount+expiry single-use time-bounded → Agent passes SPT to merchant
- For M2M sub-cent: x402 flow server quotes payment requirements client signs payment retries request facilitator verifies settles — agent answers 402 Payment Required with signed voucher within approved limit
- Merchant runs SPT through Stripe normal processor: stripe.paymentIntents.create({amount, payment_method_data: {type: "shared_payment_token", shared_payment_token: {token}}})
- AP2 Payment Mandate signals to payment network agent involved

↓

**Layer 4 — Fulfillment (merchant existing):**

Merchant runs order existing pipeline warehouse logistics customer service retains relationship buyer for refunds dispute handling post-purchase support even when agent placed order.

↓

**Layer 5 — Memory + Observability (Kafka + Memory Bank + progress.json):**

- Kafka gives stateless protocols shared durable view reality
- progress.json structured JSON not markdown + session_handoff.md for next agent enables 6-hour agents
- OKF diffable text fits engineering discipline — metric definitions runbooks can be updated via PRs reviewed owners rolled back — turns why did number change into git blame instead Slack archaeology
- Observability across MCP calls + A2A Tasks + ACP checkout sessions + AP2 mandates

**Composition: Mechanism only works when each step composes with next — shopping agent that runs MCP discovery still needs ACP or UCP checkout call, AP2 or TAP for authorization signature, settlement rail (card network Stripe x402) for actual money movement. Protocols designed to compose but composition still being negotiated real time.**

**Architecture diagram (text):**

```
User: "order shoes < $150 arrive Friday" (natural language goal)
    ↓
[Agent Gateway + Model Armor]
    ↓
Supervisor Agent (A2A)
    ├── Planner: OKF bundle policies/shipping.md → arrival Friday feasible?
    ├── Retriever (A2A Task: retrieve):
    │     MCP: product_search → Etsy trail shoes $129, Nike $149
    │     MCP: inventory_check → both in stock
    │     UCP: merchant capabilities → both support checkout, returns
    │     OKF: concepts/refund.md → page 25 bundle approval
    ├── Authorizer (A2A Task: authorize):
    │     AP2: Intent Mandate $150 footwear this week user-signed
    │     AP2: Cart Mandate exact $129 Etsy
    │     Signed Agent Card: payment_methods + auth Bearer
    │     Visa TAP: agent identity signed header
    ├── Executor (A2A Task: execute checkout):
    │     ACP: create checkout session cart $129
    │     ACP: Shared Payment Token issuance merchant-scoped amount-scoped expiry single-use
    │     ACP/MPP/x402: settlement rail selection card vs stablecoin
    │     Stripe: paymentIntents.create SPT
    │     AP2: Payment Mandate agent_involved_flag true
    └── Reporter (A2A Task: report):
          MCP: write progress.json order_id fulfillment tracking
          Kafka: durable event order_created
          Merchant: fulfillment warehouse, webhooks order confirmation
```

**For your refund agent curriculum extension:**

Existing: refund_policy_check + bundle_validation via MCP → now add refund execution via ACP/AP2

- Customer: "Refund order #12345 bundle promotion"
- Agent: checks policy page 25 via OKF/MCP → requires approval → validates bundle via MCP → creates refund checkout session via ACP (reverse SPT) → AP2 mandate proves user authorized refund → Stripe refund via SPT → progress.json + session_handoff.md

### 10. Shared Payment Token + Mandates — How Money Moves Without Exposing Cards

**Shared Payment Token (ACP core primitive):**

Instead of exposing buyer's saved card to agent, buyer's payment provider issues token scoped to specific merchant and specific amount with short expiry. Agent passes token to merchant; merchant runs it through normal processor (typically Stripe).

Properties:

- Merchant-scoped: token bound to specific merchant_id — cannot be used elsewhere
- Amount-scoped: token bound to specific dollar amount — cannot be overspent
- Time-bounded: short expiry e.g., 1 hour
- Single-use: one-time use prevents replay
- No raw card exposure: agent never sees PAN, only token

Vs traditional: Traditional checkout agent would need card number → fraud risk. SPT = capability token like OAuth but for money.

**Mandates (AP2 core primitive):**

Tamper-evident cryptographically signed credentials recording what user approved — verifiable credentials — non-repudiable receipt.

- Intent Mandate: spend within scope like under $50 on office supplies — user-signed open mandate sets constraints — proof what agent may buy? Actually intent = what user asked for
- Cart Mandate: approve these exact items — agent assembled — proof what agent may buy — finalized mandate agent signs within open mandate
- Payment Mandate: signals to payment network agent was involved — authorizes payment — what gets charged — tamper-resistant

For autonomous purchases user-signed open mandates set constraints and agent signs finalized mandates within them. AP2 defines verification responsibilities; payment processing belongs to payment processor not new AP2 settlement network.

**Verifiable authorization evidence flow:**

AP2 supplies verifiable authorization evidence — permission payment requests settlement are different parts. AI agent's permission to spend is not same as payment request or movement of money. Mastercard Agent Pay Visa TAP AP2 x402 address overlapping but different parts purchase.

- Mastercard Agent Pay = card-based program tokenized credentials enrollment identity verification authentication consumer intent checkout tokenized payload — integrators must register Mastercard issuer authorizes transaction — connects agents to card payments rather than replacing card network with new crypto
- AP2 = supplies verifiable authorization evidence — v0.2 separates Checkout Mandate proof what agent may buy from Payment Mandate authorizing payment — autonomous purchases user-signed open mandates set constraints agent signs finalized mandates within them — defines verification responsibilities
- x402 = carries payment exchange — server quotes payment requirements client signs payment retries request facilitator can verify settle it — does not prescribe single payment rail — distinguishes schemes typically settle immediately from batch settlement authorizes upfront redeems value onchain later
- Agent Pay for Machines = combines credentialing programmatically enforced spending rules with settlement across cards accounts stablecoins — opened early access Oct 20 offering buyer seller side APIs toolkit sandbox docs — builds on x402 agent answers 402 Payment Required response with signed voucher within approved limit seller verifies delivers service vouchers can be combined redeemed later

**How they compose in one purchase:**

User signs Intent Mandate "up to $150 footwear this week" → Agent discovers $129 shoes → Agent creates Cart Mandate exact items → Agent signs finalized mandates within Intent constraints → Payment provider issues SPT scoped Etsy $129 expiry 1h single-use → Agent passes SPT + mandates to merchant via ACP checkout session → Merchant verifies AP2 signatures via FIDO directory + Visa TAP signature → Merchant runs SPT through Stripe → AP2 Payment Mandate signals agent involved → Settlement via card rail or x402 stablecoin → Merchant stores mandate as non-repudiable receipt → Fulfillment existing pipeline → Order confirmation + webhooks

### 11. Node.js Production Implementation — MCP Server + A2A + ACP Checkout

**Stack you have: Node.js + Postgres + pgvector + MCP + A2A — now add ACP/AP2**

**Step 1: MCP Server with commerce tools + product feed + policy (TypeScript ~40 lines):**

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET!);
const server = new McpServer({ name: "commerce-policy-server", version: "1.0.0" });

// Existing refund tools from curriculum
server.tool("refund_policy_check", { orderId: z.string(), policyVersion: z.string().default("v2.3") }, async ({ orderId }) => ({
  content: [{ type: "text", text: `Order ${orderId} checked policy v2.3 page 25: bundle promotions require approval - never auto-refund` }]
}));

// New: Product search via OKF + pgvector
server.tool("product_search", {
  query: z.string().describe("e.g. trail-running shoes under $150"),
  maxPrice: z.number().optional(),
  category: z.string().optional()
}, async ({ query, maxPrice }) => {
  // pgvector hybrid dense+BM25+reranker over products table
  // const results = await pg.query(`SELECT * FROM products ORDER BY embedding <-> $1 LIMIT 5`, [embedding])
  return { content: [{ type: "text", text: `Found Etsy trail-shoe-123 $129 arrival Friday feasible, Nike $149` }] };
});

server.tool("inventory_check", { sku: z.string() }, async ({ sku }) => ({
  content: [{ type: "text", text: `SKU ${sku} in stock, 12 units` }]
}));

// ACP: Create checkout session with Shared Payment Token
server.tool("acp_create_checkout", {
  merchantId: z.string(),
  items: z.array(z.object({ sku: z.string(), qty: z.number(), price: z.number() })),
  total: z.number(),
  currency: z.string().default("USD"),
  ap2MandateId: z.string().describe("AP2 Intent Mandate ID proving authorization")
}, async ({ merchantId, items, total, ap2MandateId }) => {
  // 1. Verify AP2 mandate (FIDO directory)
  // const mandate = await verifyAP2Mandate(ap2MandateId); // check signature, expiry, constraints
  // 2. Issue Shared Payment Token via Stripe
  const spt = await stripe.paymentIntents.create({
    amount: total,
    currency: "usd",
    // In real ACP: payment_method_data type shared_payment_token
    // Simplified: create ephemeral token scoped merchant+amount
    metadata: { merchant_id: merchantId, ap2_mandate_id: ap2MandateId, acp_version: "2026-04-17" }
  });
  return {
    content: [{ 
      type: "text", 
      text: JSON.stringify({
        checkout_session_id: `cs_acp_${Date.now()}`,
        merchant_id: merchantId,
        cart: { items, total },
        shared_payment_token: { token: spt.id, merchant_id: merchantId, amount: total, expires_at: new Date(Date.now()+3600*1000).toISOString(), single_use: true },
        ap2_mandate_verified: true,
        status: "ready_for_merchant"
      }, null, 2)
    }]
  };
});

// AP2: Create Intent Mandate
server.tool("ap2_create_intent_mandate", {
  userId: z.string(),
  maxAmount: z.number(),
  category: z.string(),
  merchants: z.array(z.string()),
  expiresInDays: z.number().default(7)
}, async ({ userId, maxAmount, category, merchants, expiresInDays }) => {
  const intentMandate = {
    id: `intent_${Date.now()}`,
    user_id: userId,
    constraints: { max_amount: maxAmount, currency: "USD", category, merchants, expires_at: new Date(Date.now()+expiresInDays*86400000).toISOString() },
    signature: `user_signed_jwt_simulated_${userId}`, // Real: FIDO wallet signs JWT
    issuer: "fido_ap2_wallet"
  };
  // Store in Postgres ap2_mandates table
  return { content: [{ type: "text", text: JSON.stringify(intentMandate, null, 2) }] };
});

await server.run(); // stdio default or HTTP+SSE adapter, stateless July 2026 spec
```

Drop into Claude Desktop or Cursor mcp.json config restart client tools live. Model will call when user says "order shoes under $150".

**Step 2: A2A Agent Card with payments (publish at /.well-known/agent-card.json):**

```json
{
  "name": "Commerce Specialist Agent",
  "description": "Handles product discovery, refund policy, and ACP checkout",
  "url": "https://agents.example.com/commerce-agent",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "multiTenancy": true
  },
  "authentication": {
    "schemes": ["Bearer", "OAuth2"]
  },
  "payment_methods": {
    "supported": ["shared_payment_token", "ap2_mandate", "x402", "card_token"],
    "processors": ["stripe", "visa", "mastercard"],
    "ap2_version": "0.2",
    "acp_version": "2026-04-17"
  },
  "skills": [
    {
      "id": "product_search",
      "name": "Product Search",
      "description": "Searches product catalog via pgvector OKF bundle",
      "tags": ["commerce", "discovery"]
    },
    {
      "id": "acp_checkout",
      "name": "ACP Checkout",
      "description": "Creates ACP checkout session with Shared Payment Token and AP2 mandate verification",
      "tags": ["commerce", "checkout", "acp"]
    },
    {
      "id": "refund_policy_check",
      "name": "Refund Policy Check",
      "description": "Checks order against refund policy v2.3 page 25",
      "tags": ["refund", "policy"]
    }
  ]
}
```

Signed Agent Card: v1.0 added signed Agent Cards for cryptographic identity verification and expanded support for enterprise multi-tenancy — merchant verifies signature against FIDO directory.

**Step 3: A2A Task delegation + ACP checkout (Python pseudo using A2A SDK):**

```python
from a2a import A2AClient
import stripe

client = A2AClient()
# Discover via Agent Card
agent_card = await client.fetch_agent_card("https://agents.example.com/.well-known/agent-card.json")

# Step 1: Authorize via AP2
intent_mandate = await client.create_task(
  agent_url=agent_card.url,
  skill_id="ap2_create_intent_mandate",
  input={"userId": "user_789", "maxAmount": 15000, "category": "footwear", "merchants": ["etsy", "nike"], "expiresInDays": 7}
)

# Step 2: Discover products via MCP
search_task = await client.create_task(
  agent_url=agent_card.url,
  skill_id="product_search",
  input={"query": "trail-running shoes under $150 arrive Friday", "maxPrice": 150}
)

# Step 3: Checkout via ACP with AP2 mandate verification + SPT
checkout_task = await client.create_task(
  agent_url=agent_card.url,
  skill_id="acp_checkout",
  input={
    "merchantId": "etsy_456",
    "items": [{"sku": "trail-shoe-123", "qty": 1, "price": 12900}],
    "total": 12900,
    "currency": "USD",
    "ap2MandateId": intent_mandate.id
  }
)

# Track lifecycle submitted→working→completed
async for update in client.stream_task(checkout_task.id):
  print(f"Task {update.task_id} state: {update.state}")
  if update.state == "completed":
    spt = update.artifacts["shared_payment_token"]
    # Merchant side: run SPT through Stripe
    payment_intent = stripe.PaymentIntent.create(
      amount=spt["amount"],
      currency="usd",
      payment_method_data={"type": "shared_payment_token", "shared_payment_token": {"token": spt["token"]}}
    )
    print(f"Order created: {update.artifacts['checkout_session_id']}, Payment: {payment_intent.id}")
  elif update.state == "input-required":
    await client.provide_input(checkout_task.id, {"approval": "yes"})
  elif update.state == "failed":
    print(f"Failed: {update.error}")
```

**Step 4: Merchant side (Node.js + Stripe):**

```javascript
import express from "express";
const app = express();

app.post("/acp/checkout", async (req, res) => {
  const { shared_payment_token, cart_mandate, ap2_mandate } = req.body;
  
  // 1. Verify AP2 mandates (FIDO directory)
  const ap2Valid = await verifyAP2Mandate(ap2_mandate); // signature, expiry, merchant_id, amount
  if (!ap2Valid) return res.status(401).json({ error: "Invalid AP2 mandate" });
  
  // 2. Verify Visa TAP agent identity header
  const tapValid = await verifyVisaTAP(req.headers["x-visa-tap-signature"]);
  
  // 3. Run SPT through Stripe (existing processor)
  const paymentIntent = await stripe.paymentIntents.create({
    amount: shared_payment_token.amount,
    currency: "usd",
    payment_method_data: {
      type: "shared_payment_token",
      shared_payment_token: { token: shared_payment_token.token }
    },
    metadata: {
      ap2_intent_id: ap2_mandate.intent_id,
      agent_id: cart_mandate.agent_id,
      acp_version: "2026-04-17",
      ap2_version: "0.2"
    }
  });
  
  // 4. Store mandate as non-repudiable receipt for disputes
  await pg.query(`INSERT INTO ap2_receipts (intent_id, cart_id, payment_intent_id, amount, merchant_id) VALUES ($1,$2,$3,$4,$5)`, 
    [ap2_mandate.id, cart_mandate.id, paymentIntent.id, shared_payment_token.amount, shared_payment_token.merchant_id]);
  
  // 5. Fulfillment existing pipeline
  const order = await createOrder({ cart: req.body.cart, paymentIntentId: paymentIntent.id });
  
  // 6. Webhooks order confirmation
  await sendWebhook({ event: "order.created", order_id: order.id, checkout_session_id: req.body.checkout_session_id });
  
  res.json({ order_id: order.id, status: "fulfilled", payment_intent_id: paymentIntent.id });
});
```

**Step 5: For M2M micro-payments via x402:**

```javascript
// Server returns 402 Payment Required
app.get("/api/research", async (req, res) => {
  const ap2Mandate = req.headers["x-ap2-mandate"];
  if (!ap2Mandate) {
    // Quote payment requirements
    return res.status(402).json({
      payment_requirements: {
        amount: 1, // 1 cent sub-cent
        currency: "USD",
        rail: "x402",
        stablecoin: "USDC",
        network: "base"
      },
      ap2_required: true
    });
  }
  // Client signs payment and retries request with signed payment
  // Facilitator verifies and settles
  const verified = await x402Facilitator.verify(req.headers["x-x402-payment"]);
  if (verified) {
    await x402Facilitator.settle(req.headers["x-x402-payment"]);
    res.json({ data: "research results" });
  }
});
```

### 12. Database Schema — Postgres + pgvector + ClickHouse for Agent Commerce

**Postgres (core transactional):**

```sql
-- Products for MCP product_search via pgvector hybrid dense+BM25+reranker
CREATE TABLE products (
  id TEXT PRIMARY KEY,
  sku TEXT UNIQUE,
  name TEXT,
  description TEXT,
  price INT, -- cents
  currency TEXT DEFAULT 'USD',
  merchant_id TEXT,
  embedding VECTOR(768), -- pgvector for semantic search
  metadata JSONB, -- OKF path, tags, arrival estimates
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON products USING ivfflat (embedding vector_l2_ops);

-- AP2 Mandates (authorization layer)
CREATE TABLE ap2_mandates (
  id TEXT PRIMARY KEY,
  type TEXT CHECK (type IN ('intent', 'cart', 'payment')),
  user_id TEXT,
  intent_id TEXT REFERENCES ap2_mandates(id), -- cart references intent
  cart_id TEXT REFERENCES ap2_mandates(id), -- payment references cart
  constraints JSONB, -- max_amount, category, merchants, expires_at
  amount INT,
  merchant_id TEXT,
  agent_id TEXT,
  signature TEXT, -- user_signed_jwt or agent_signed
  issuer TEXT, -- fido_ap2_wallet
  status TEXT DEFAULT 'active',
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- ACP Checkout Sessions
CREATE TABLE acp_checkout_sessions (
  id TEXT PRIMARY KEY,
  merchant_id TEXT,
  user_id TEXT,
  cart JSONB, -- items sku qty price
  total INT,
  currency TEXT,
  shared_payment_token JSONB, -- token, merchant_id, amount, expires_at, single_use
  ap2_intent_id TEXT REFERENCES ap2_mandates(id),
  ap2_cart_id TEXT REFERENCES ap2_mandates(id),
  ap2_payment_id TEXT REFERENCES ap2_mandates(id),
  stripe_payment_intent_id TEXT,
  status TEXT CHECK (status IN ('pending', 'ready_for_merchant', 'paid', 'fulfilled', 'failed', 'refunded')),
  ap2_receipt_id TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Orders (fulfillment)
CREATE TABLE orders (
  id TEXT PRIMARY KEY,
  checkout_session_id TEXT REFERENCES acp_checkout_sessions(id),
  merchant_id TEXT,
  user_id TEXT,
  items JSONB,
  total INT,
  stripe_payment_intent_id TEXT,
  status TEXT,
  tracking_number TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- AP2 Receipts non-repudiable for disputes
CREATE TABLE ap2_receipts (
  id TEXT PRIMARY KEY,
  intent_id TEXT,
  cart_id TEXT,
  payment_intent_id TEXT,
  amount INT,
  merchant_id TEXT,
  agent_id TEXT,
  mandate_signatures JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Agent Cards registry
CREATE TABLE agent_cards (
  url TEXT PRIMARY KEY,
  name TEXT,
  version TEXT,
  capabilities JSONB,
  authentication JSONB,
  payment_methods JSONB,
  skills JSONB,
  signature TEXT, -- signed Agent Card v1.0 crypto verification
  last_fetched TIMESTAMP DEFAULT NOW()
);
```

**ClickHouse (analytics, observability):**

```sql
CREATE TABLE agent_commerce_events (
  event_id UUID,
  timestamp DateTime,
  user_id String,
  agent_id String,
  merchant_id String,
  event_type Enum('discovery', 'authorization', 'payment', 'fulfillment', 'refund'),
  protocol Enum('acp', 'ap2', 'x402', 'mpp', 'ucp', 'mcp', 'a2a', 'visa_tap'),
  checkout_session_id String,
  ap2_mandate_id String,
  amount Int32,
  currency String,
  status String,
  latency_ms Int32,
  error String,
  metadata String
) ENGINE = MergeTree() ORDER BY timestamp;
```

**For refund agent curriculum:**

Existing tables orders + new acp_checkout_sessions for refund execution via reverse SPT + ap2_mandates proving refund authorization + progress.json.

### 13. Security, Trust, Fraud — Mandates, Signed Agent Cards, TAP

**Why authorization layer is most contested:**

Most agent-fraud risk concentrates at authorization layer — agent proves to merchant real user delegated purchase and merchant proves to network agent legitimate.

**AP2 security:**

- Tamper-evident cryptographically signed mandates — verifiable credentials — non-repudiable receipt stored by merchant for disputes
- User-signed open mandates set constraints agent signs finalized mandates within them — agent cannot exceed Intent constraints (max amount, category, merchants, expiry)
- Verification responsibilities defined — payment processing belongs to processor not new AP2 settlement network
- Donated to FIDO Alliance April 2026 — leverages FIDO identity infrastructure
- Human Not Present v0.2 adds autonomous buying within pre-authorized limits without user actively present — critical enterprise reorder agents M2M but requires strict open mandate constraints
- Payment-agnostic — works with cards bank rails stablecoins — extension wires to x402 stablecoin payments

**Visa TAP:**

- Cryptographic agent identity for merchant-side trust — signs agent identity into HTTP request headers merchants verify signature against Visa directory
- Launched Oct 14 2025 with Cloudflare — enrollment identity verification authentication consumer intent
- Co-developed Verifiable Intent March 5 2026 with Google as authorization-record standard aligned AP2

**Mastercard Agent Pay:**

- Tokenized payment credentials enrollment identity verification authentication consumer intent checkout tokenized payload — integrators must register Mastercard issuer authorizes transaction — connects agents to card payments rather than replacing card network new cryptocurrency
- Agent Pay for Machines June 10 2026 combines credentialing programmatically enforced spending rules with settlement across cards accounts stablecoins — opened early access Oct 20 offering buyer seller side APIs toolkit sandbox docs — builds on x402 agent answers 402 Payment Required response with signed voucher within approved limit seller verifies delivers service vouchers can be combined redeemed later — still pilot not commercially
- Programmable virtual cards Lithic Stripe Issuing Marqeta Highnote Ramp Brex bridge between agentic protocols and existing card-network universe — agent can spin up per merchant or per session

**A2A Signed Agent Cards:**

- v1.0 April 2026 added signed Agent Cards for cryptographic identity verification expanded enterprise multi-tenancy — merchant verifies agent card signature against registry before accepting checkout
- Authentication schemes Bearer OAuth2
- Payment_methods field in Agent Card — supported rails, processors, AP2 version, ACP version

**Trust layer 7:**

HUMAN Security Riskified Forter Signifyd Kasada DataDome Akamai Cloudflare — fraud bot detection agent verification — Agentic Commerce Consortium formed Basis Theory Lithic Crossmint Skyfire Rye Channel3 others publishing security standards across layer.

**Security checklist:**

1. Never expose raw PAN to agent — use SPT merchant-scoped amount-scoped expiry single-use
2. Verify AP2 mandate signature via FIDO directory before running SPT — check expiry, merchant_id, amount, constraints
3. Verify Visa TAP signature header against Visa directory
4. Verify signed Agent Card signature against registry
5. Store AP2 mandates as non-repudiable receipts for disputes
6. Open mandates must have strict constraints max_amount category merchants expires_at — prevent open-ended authorization
7. Human Not Present requires additional approval policy — enterprise agents need budget limits
8. Virtual cards per merchant/session via Lithic/Stripe Issuing — limit blast radius
9. Observability across all layers — log AP2 intent_id cart_id payment_id checkout_session_id for audit
10. Model Armor + Agent Gateway — policy enforcement who can delegate what to whom

### 14. Failure Modes & What Went Wrong — Why Instant Checkout Retired

**Why OpenAI retired Instant Checkout March 2026 after ~12 Shopify merchants:**

- Only about dozen Shopify merchants went live before OpenAI retired Instant Checkout March 2026 in favor dedicated retailer apps (Walmart Target Instacart) inside ChatGPT
- OpenAI said first version Instant Checkout not flexible enough and moved ChatGPT focus to product discovery with merchants using own checkout — March 2026 announcement expanding ACP to product discovery letting merchants use own checkout experiences merchants now use ACP to share product feeds promotions with ChatGPT
- OpenAI pivoted from Instant Checkout only ~12 active merchants out of millions to visual product discovery with checkout on retailer site — where conversion lives matters
- Merchants want control checkout upsells analytics — ACP now routes most buyers back to merchant keeps checkout upsells analytics intact

**Lesson for production:**

Don't try to own checkout — own discovery + authorization + payment token. Fulfillment merchant existing pipeline. ACP current discovery-first: AI handles product research intent merchants retain control checkout under ACP — buyer routed to merchant site cart pre-filled via ACP — merchant existing checkout handles payment. Conversion lives at merchant.

**Other failure modes:**

- Protocol fragmentation — most merchants need support more than one — 6 protocols overlapping different parts — composition still being negotiated real time — conceptual purchase flow does not imply all four offerings run together
- Agentic traffic converts 15-30% 5-10x improvement but requires merchant enablement product feeds standardized Salsify Syndigo Akeneo
- Authorization fraud — without AP2 mandates + TAP + signed Agent Cards agent could spend arbitrarily — need FIDO directory verification
- Open mandates without strict constraints — human not present purchases need constraints max_amount category merchants expires_at
- SPT replay — must be single-use merchant-scoped amount-scoped expiry — check in Stripe
- Cost — 4% OpenAI platform fee + ~3% Stripe = 7% total autonomous agent-led conversions — merchants must factor — durable value will accrue settlement rails stablecoin issuers payment facilitators rather than open-source protocols themselves — same logic TCP/IP captured no rents while Akamai Cloudflare AWS captured plenty — thesis contested but informs strategic acquirers positioning
- Browser robot layer fallback — when merchant has not adopted ACP or UCP agent still needs way complete purchase — Rye Induced AI Henry Labs automation fills checkout forms merchant actual site — brittle

**What to build for resilience:**

- Support both ACP and UCP for discovery checkout — composes with AP2 payments MCP tool access
- Always verify AP2 mandate + TAP + signed Agent Card — don't trust agent identity alone
- Use virtual cards per merchant/session to limit blast radius
- Store mandates as non-repudiable receipts
- Implement budget limits in Intent Mandates — max_amount category merchants expires_at
- Fallback to browser automation Rye when ACP/UCP not supported but log as brittle path
- Observability — ClickHouse events for discovery authorization payment fulfillment — trace checkout_session_id ap2_mandate_id across layers

### 15. Future — $3-5T by 2030, Stablecoins Default for M2M

**Market projections:**

- McKinsey QuantumBlack Oct 2025: $3T-$5T global retail spend orchestrated by agents by 2030 up to $1T US B2C alone
- Juniper April 2026: $1.5T agentic commerce spend 2030 tighter view; June 2026 study $8B total agentic transaction value 2026 — five-to-six-year compounding curve not near-term inflection
- Global agentic commerce volume by 2030 McKinsey — 2026 year infrastructure standards being locked in — decisive happened 2024 holiday shopping season NRF 2026 consensus clear agentic commerce moved from experiment to commercial infrastructure
- Agentic traffic converts 15-30% 5-10x improvement traditional benchmarks Q1 2026 data — Adobe 4,700% YoY jump generative-AI traffic US retail July 2024-July 2025

**Stablecoins default settlement currency for M2M:**

- x402 processed 165M agent transactions first months — stablecoins default for machine-to-machine payments
- Reason: sub-cent transactions, immediate settlement, batch settlement authorizes upfront redeems value onchain later, no card network fees, programmable
- Coinbase Developer Platform supplied wallet infrastructure Base supplied onchain settlement network BVNK handled fiat stablecoin payment settlement — example marketing agency Hype approved one budget agent bought research from AIsa and eight images through Cloudflare AI Gateway nine payments two merchants
- Insignia April 2026 analysis: durable value will accrue to settlement rails stablecoin issuers payment facilitators rather than open-source protocols themselves — TCP/IP captured no rents while Akamai Cloudflare AWS captured plenty

**Protocol convergence:**

- AP2 donated to FIDO Alliance April 2026 — now governance at FIDO — adds human not present purchases
- UCP spec Aug 25 2026 stable — Google positioning universal rather than competitor ACP — composes with AP2 payments MCP tool access
- ACP spec April 17 2026 stable — Apache 2.0 — added carts product feed API MCP binding — discovery-first after March 2026 pivot
- x402 foundation operational July 14 2026 — V2 Dec 11 2025 — distinguishes immediate vs batch settlement
- MPP March 18 2026 — metered per-call billing APIs stablecoin fiat cards Klarna Affirm via Shared Payment Tokens
- Visa TAP Oct 14 2025 + Mastercard Agent Pay April 29 2025 + Agent Pay for Machines June 10 2026 early access Oct 20 APIs toolkit sandbox docs pilot not commercially — combining credentialing programmatically enforced spending rules settlement across cards accounts stablecoins building on x402

**What changes for your refund agent:**

- Today: refund_policy_check + bundle_validation via MCP
- Tomorrow: refund execution via ACP reverse SPT + AP2 mandate proving user authorized refund + Stripe refund + progress.json + ClickHouse audit
- Future: agent not only checks refund policy but executes refund autonomously within Intent Mandate constraints — "You can refund up to $500 for bundle promotions this week" — AP2 mandate + SPT + merchant fulfillment refund pipeline

**Production mantra 2026 extended:**

Stop asking whether A2A will replace MCP. It won't. A2A and MCP solve different production problems. Now stop asking whether ACP will replace AP2 or x402. They won't. They solve different layers:

- MCP for agent-to-tool/context access (hands) — product search, inventory, policy
- A2A for agent-to-agent coordination (voices) — supervisor → retriever → authorizer → executor → reporter
- AP2 for authorization (proof) — Intent + Cart + Payment Mandates cryptographically signed FIDO — human authorized
- ACP for checkout (handshake) — Shared Payment Token merchant-scoped amount-scoped expiry single-use — no raw card exposure
- x402/MPP for settlement (movement) — how money moves inside web request — stablecoins default M2M
- UCP for full journey discovery→post-purchase — product discovery capability negotiation plus checkout handoff
- Visa TAP + Mastercard Agent Pay for trust — cryptographic agent identity + tokenized credentials
- Kafka + Memory Bank for memory — stateless protocols shared durable view reality
- OKF for knowledge — curated stable knowledge bundle path=ID links=graph portable Git-reviewable

That is stack serious AI teams should be designing for agentic commerce now.

**Bottom line:** Agentic commerce is commerce carried out by AI agents on person's behalf: agent discovers products decides completes purchase using protocols ACP checkout handshake AP2 authorization layer person authorizes agent once within set limits token proves consent without exposing banking data. ACP is agent-ready checkout built jointly OpenAI Stripe to make existing online checkouts navigable by AI agent instead human filling form lets business define how agent can complete purchase using merchant own existing commerce payment stack no separate agent-only checkout build live with real merchants Etsy Coach Kate Spade Urban Outfitters brands as of 2026. AP2 is authorization layer Google's Agent Payments Protocol designed prove user organization actually authorized agent to make purchase uses tamper-resistant cryptographically signed mandates to capture intent cart details payment authorization payment-method agnostic can work with cards bank rails stablecoins announced Sept 2025 with 60+ orgs. Mechanism only works when each step composes next — shopping agent that runs MCP for discovery still needs ACP or UCP for checkout call AP2 or TAP for authorization signature settlement rail card network Stripe x402 for actual money movement. Protocols designed to compose but composition still being negotiated real time. 2026 year infrastructure standards being locked in.

---
*Module: Agentic Commerce Protocol + AP2 + Agent Payments — Full Production Guide — Part of Advanced Agentic AI Curriculum — v1.0 — October 2026*
*Reference: ACP Agentic Commerce Protocol OpenAI Stripe Sept 29 2025 Apache 2.0 spec April 17 2026 stable added carts product feed API MCP binding Etsy first merchant 12 Shopify merchants went live before retired Instant Checkout March 2026 in favor Walmart Target Instacart apps inside ChatGPT now discovery-first AI handles product research intent merchants retain control checkout under ACP routes buyers back to merchant keeps checkout upsells analytics intact where conversion lives 4% OpenAI fee + 3% Stripe = 7% total autonomous conversions Shared Payment Token SPT scoped merchant amount expiry single-use no raw card exposure checkout sessions cart product feed delegated payment delegated auth orders webhooks live Coach Kate Spade Urban Outfitters, UCP Universal Commerce Protocol Google Jan 2026 NRF Sundar Pichai keynote spec Aug 25 2026 Shopify Walmart Target Best Buy Etsy PayPal Visa Stripe Amex co-developed discovery checkout post-purchase capability negotiation composes AP2 MCP universal rather competitor, AP2 Agent Payments Protocol Google Sept 16 2025 60+ orgs Coinbase Mastercard PayPal Revolut Salesforce Worldpay Adyen Amex Etsy more than 60 donated FIDO Alliance April 2026 v0.2 April 28 2026 separates Checkout Mandate proof what agent may buy from Payment Mandate authorizing payment user-signed open mandates constraints agent signs finalized within them verification responsibilities defined payment processing belongs to processor not new settlement network authorization layer proof user authorized what agent buys on any rail payment-agnostic framework cards debit stablecoins real-time bank transfers establishes framework users merchants payments providers transact confidence does not move money hands off to rail extension wires to x402 stablecoin payments three mandates Intent Cart Payment cryptographically signed verifiable credentials tamper-evident non-repudiable receipt human not present HNP autonomous buying within pre-authorized limits PayPal partnership live sample using x402-compatible payments Verifiable Intent March 5 2026 Mastercard Google co-developed authorization-record standard aligned AP2, x402 Coinbase May 6 2025 V2 Dec 11 2025 foundation operational July 14 2026 server quotes payment requirements client signs retries facilitator verifies settles does not prescribe single rail immediate vs batch settlement 165M txns first months stablecoins default M2M how money moves inside web request, MPP Machine Payments Protocol Stripe Tempo March 18 2026 settlement sessions streaming metered per-call billing APIs stablecoin fiat cards Klarna Affirm via Shared Payment Tokens agent wallet must hold supported method agent-to-business purchases scale, MCP Anthropic Nov 2024 donated AAIF Dec 2025 co-founded Block OpenAI upstream every commerce protocol agent-to-tool data plane search catalog inventory return policy, A2A Google April 2025 production 150+ orgs Azure AI Foundry Bedrock AgentCore Salesforce agent-to-agent delegation shopping agent delegates price comparison specialist checkout merchant-side agent, Visa TAP Trusted Agent Protocol Visa Cloudflare Oct 14 2025 cryptographic agent identity signs identity into HTTP headers verify signature against Visa directory enrollment identity verification authentication consumer intent, Mastercard Agent Pay April 29 2025 tokenized credentials enrollment identity verification checkout tokenized payload integrators register Mastercard issuer authorizes connects agents to card payments not replacing card network crypto Agent Pay for Machines June 10 2026 credentialing programmatically enforced spending rules settlement cards accounts stablecoins early access Oct 20 buyer seller side APIs toolkit sandbox docs builds on x402 agent answers 402 Payment Required signed voucher within approved limit seller verifies delivers vouchers combined redeemed later pilot not commercially marketing agency Hype example one budget bought research from AIsa eight images Cloudflare AI Gateway nine payments two merchants Coinbase Developer Platform wallet Base onchain BVNK fiat stablecoin settlement, 7-layer stack Rye framework AI platforms agent surfaces OpenAI Google Anthropic Perplexity Amazon Microsoft Meta protocols standards ACP UCP AP2 MCP A2A Visa TAP payments identity Visa Mastercard PayPal Stripe Adyen Checkout.com Basis Theory $33M Series B Oct 2025 Skyfire $9.5M Nekuda $5M seed $47.5M total agent-payment infrastructure card issuance Lithic Stripe Issuing Marqeta Highnote Ramp Brex programmable virtual cards per merchant/session bridge to card-network checkout execution browser robot Rye Induced AI Henry Labs fills checkout forms merchant actual site Rye $14M merchant enablement discovery Shopify commercetools BigCommerce Adobe SAP Salsify Syndigo Akeneo product feeds trust security HUMAN Security Riskified Forter Signifyd Kasada DataDome Akamai Cloudflare Agentic Commerce Consortium Basis Theory Lithic Crossmint Skyfire Rye Channel3 security standards, 4-step lifecycle discovery MCP UCP authorization AP2 Visa TAP Mastercard Agent Pay payment ACP SPT x402 MPP fulfillment merchant existing pipeline retains relationship refunds dispute handling post-purchase support composes, Market McKinsey $3-5T 2030 up to $1T US B2C Juniper $1.5T 2030 $8B total agentic transaction value 2026 Adobe 4700% YoY generative-AI traffic July 2024-July 2025 agentic traffic converts 15-30% 5-10x traditional benchmarks Q1 2026, Production equation Cross-Cloud Lakehouse × Knowledge Catalog + MCP Server + A2A Swarm @ TPU v8i + Agent Gateway Model Armor + Vertex AI Memory Bank + ACP Checkout + AP2 Mandates + x402 Settlement = Production-Ready Agentic Commerce OS, Implementation Node.js TypeScript McpServer refund_policy_check product_search inventory_check acp_create_checkout ap2_create_intent_mandate pgvector hybrid dense BM25 reranker Stripe paymentIntents shared_payment_token metadata acp_version ap2_version verification FIDO directory Visa TAP signature A2A Agent Card payment_methods supported shared_payment_token ap2_mandate x402 card_token processors stripe visa mastercard ap2_version 0.2 acp_version 2026-04-17 skills product_search acp_checkout refund_policy_check signed Agent Card v1.0 crypto verification enterprise multi-tenancy A2AClient fetch_agent_card create_task stream_task submitted working completed input-required failed Stripe PaymentIntent create payment_method_data shared_payment_token checkout_session cart, Merchant side Express /acp/checkout verifyAP2Mandate verifyVisaTAP stripe.paymentIntents.create shared_payment_token ap2_receipts non-repudiable createOrder sendWebhook order.created, x402 402 Payment Required server quotes payment_requirements amount currency rail x402 stablecoin USDC network base ap2_required client signs retries x402Facilitator verify settle research results, Postgres products sku name description price embedding VECTOR metadata pgvector ivfflat ap2_mandates id type intent cart payment user_id intent_id cart_id constraints amount merchant_id agent_id signature issuer status expires_at acp_checkout_sessions id merchant_id user_id cart total currency shared_payment_token ap2_intent_id cart_id payment_id stripe_payment_intent_id status pending ready_for_merchant paid fulfilled failed refunded ap2_receipt_id orders checkout_session_id merchant_id items total tracking_number ap2_receipts intent_id cart_id payment_intent_id amount merchant_id agent_id mandate_signatures agent_cards url name version capabilities authentication payment_methods skills signature last_fetched ClickHouse agent_commerce_events event_id timestamp user_id agent_id merchant_id event_type discovery authorization payment fulfillment refund protocol acp ap2 x402 mpp ucp mcp a2a visa_tap checkout_session_id ap2_mandate_id amount currency status latency_ms error metadata, Security SPT merchant-scoped amount-scoped expiry single-use no raw PAN capability token like OAuth but for money mandates tamper-evident verifiable credentials non-repudiable receipt open mandates strict constraints max_amount category merchants expires_at prevent open-ended HNP requires additional approval policy enterprise budget limits virtual cards per merchant/session Lithic Stripe Issuing limit blast radius observability log intent_id cart_id payment_id checkout_session_id audit Model Armor Agent Gateway policy who can delegate what, Failure modes Instant Checkout retired March 2026 ~12 Shopify merchants out of millions first version not flexible enough moved focus product discovery merchants own checkout ~12 active merchants fragmentation 6 protocols overlapping composition negotiated real time conceptual flow does not imply all four run together agentic traffic 15-30% requires merchant enablement product feeds Salsify Syndigo Akeneo authorization fraud without AP2 mandates TAP signed Agent Cards open mandates without constraints HNP SPT replay single-use merchant-scoped amount-scoped expiry check Stripe cost 7% durable value accrue settlement rails stablecoin issuers payment facilitators rather than open-source protocols TCP/IP captured no rents while Akamai Cloudflare AWS captured plenty contested strategic acquirers positioning browser robot fallback Rye Induced AI Henry Labs brittle, Future $3-5T 2030 $1.5T Juniper $8B 2026 4700% YoY 15-30% conversion stablecoins default M2M 165M txns sub-cent immediate batch settlement no card fees programmable Base onchain BVNK example Hype one budget nine payments two merchants Coinbase wallet Base settlement, Stack final MCP hands product search inventory policy A2A voices supervisor retriever authorizer executor reporter AP2 proof Intent Cart Payment mandates FIDO HNP ACP handshake SPT merchant-scoped amount-scoped expiry single-use no raw card exposure x402 MPP settlement movement money inside web request stablecoins default M2M UCP full journey discovery post-purchase Visa TAP Mastercard Agent Pay trust cryptographic identity tokenized credentials Kafka Memory Bank memory stateless protocols shared durable view OKF knowledge curated bundle path ID links graph portable Git-reviewable, Bottom line agentic commerce commerce carried out AI agents person's behalf agent discovers products decides completes purchase using protocols ACP checkout handshake AP2 authorization layer person authorizes agent once within set limits token proves consent without exposing banking data ACP agent-ready checkout built jointly OpenAI Stripe make existing online checkouts navigable by AI agent instead human filling form lets business define how agent can complete purchase using merchant own existing commerce payment stack no separate agent-only checkout build live real merchants Etsy Coach Kate Spade Urban Outfitters brands as of 2026 AP2 authorization layer Google's Agent Payments Protocol designed prove user organization actually authorized agent to make purchase uses tamper-resistant cryptographically signed mandates capture intent cart details payment authorization payment-method agnostic can work with cards bank rails stablecoins announced Sept 2025 60+ orgs mechanism only works when each step composes next shopping agent that runs MCP for discovery still needs ACP or UCP for checkout call AP2 or TAP for authorization signature settlement rail card network Stripe x402 for actual money movement protocols designed to compose but composition still being negotiated real time 2026 year infrastructure standards being locked in*
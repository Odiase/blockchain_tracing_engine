# AlphaTrace: JSU Research Upgrade Plan

## 1. Purpose

This document defines a technically realistic upgrade path for AlphaTrace, an existing prototype for examining suspected USDT ERC-20 fund movements on Ethereum. The immediate objective is to strengthen the prototype as a research foundation for a proposed master's study in Computer Science and Technology at Jiangsu University (JSU).

The upgrade must distinguish:
- **Existing baseline:** the currently implemented one-hop transaction retrieval, temporal filtering, Neo4j wallet graph, and weighted behavioural heuristics.
- **Planned improvements:** bounded multi-hop tracing, stronger transaction validation, reproducible graph records, corrected heuristic calculations, and systematic evaluation.
- **Research questions:** questions to be investigated through implementation and experiments, not claims of proven effectiveness.

No performance, accuracy, or fraud-detection result should be claimed until it has been measured on a documented dataset.

## 2. Proposed research title

**AlphaTrace: A Graph-Based Framework for Temporal Cryptocurrency Fund-Flow Tracing and Explainable Risk Assessment on Ethereum**

## 3. Research problem

Public blockchain ledgers expose transaction records, but investigating suspicious fund movements still requires analysts to retrieve, validate, order, and relate large numbers of transfers. A wallet-level view can obscure downstream movement across multiple addresses. In addition, heuristic risk scores can be difficult to interpret or reproduce if their inputs, time windows, and calculation rules are not explicit.

This project investigates whether a bounded, graph-based workflow combining temporal transaction analysis and explainable behavioural indicators can improve the organisation and examination of suspicious USDT fund flows on Ethereum.

## 4. Aim

To design, implement, and evaluate a graph-based prototype for bounded tracing of USDT ERC-20 transfers on Ethereum and explainable assessment of selected fund-movement behaviours.

## 5. Objectives

1. Audit and stabilise the existing transaction-ingestion and one-hop tracing workflow.
2. Implement bounded multi-hop expansion with configurable depth, cycle prevention, request limits, and deterministic traversal rules.
3. Model wallet-to-wallet transfers with sufficient metadata to support reproducible temporal analysis.
4. Refine behavioural indicators for balance dominance, rapid movement, and known-service exposure, documenting their assumptions and limitations.
5. Produce an explainable risk report showing each indicator, its evidence, contribution, and final score.
6. Evaluate tracing coverage, execution cost, graph growth, and scoring behaviour using a controlled, documented transaction dataset.

## 6. Research questions

- **RQ1:** How can bounded graph traversal represent downstream USDT fund movement from a specified transaction while controlling graph expansion?
- **RQ2:** Which temporal and transaction-level features can be used to construct transparent behavioural indicators for suspicious fund-flow examination?
- **RQ3:** How do traversal depth and graph-expansion limits affect tracing coverage, execution time, and API request volume?
- **RQ4:** To what extent can the proposed risk assessment produce reproducible and interpretable explanations for the observed transaction patterns?

These questions concern investigative support, not proof that an address or person committed fraud.

## 7. Scope and boundaries

### Included
- Ethereum Mainnet.
- USDT ERC-20 transfer events.
- A user-supplied starting wallet and reference transaction.
- Bounded downstream traversal of transfer relationships.
- Directed, time-aware wallet transaction graphs.
- Three initial behavioural dimensions: balance dominance, rapid movement, and interaction with a curated list of known exchange/service addresses.
- Explainable outputs and repeatable experiments.

### Excluded from the initial study
- Claims of universal cryptocurrency fraud detection.
- Attribution of real-world identities to wallet owners.
- Definitive determination that a wallet is malicious.
- All-chain or all-token coverage.
- Unbounded recursive tracing.
- Machine-learning classification unless a suitable labelled dataset is later established.
- Claims of tracing the exact same token units across addresses without a defensible asset-flow accounting model.

A transfer graph records observed movements of fungible tokens. It does not, by itself, prove that a particular unit of USDT was transferred onward when a wallet has multiple incoming and outgoing flows.

## 8. Proposed system architecture

1. **Input and validation layer**
   - Validate wallet addresses and transaction hashes.
   - Validate that the reference transaction is on the supported chain and involves the configured USDT contract.
   - Confirm that the supplied victim/source and target addresses match the relevant transfer event.
   - Normalise addresses for comparisons while preserving canonical display forms.

2. **Transaction ingestion layer**
   - Retrieve ERC-20 transfer events from the selected data provider.
   - Handle pagination, rate limits, timeouts, malformed responses, and provider errors explicitly.
   - Store raw integer token amounts and token decimals; convert to human-readable decimal values only for presentation.
   - Record block number, transaction hash, transaction index where available, log index, timestamp, sender, recipient, token contract, and chain identifier.

3. **Temporal and traversal layer**
   - Order transfers using block number and log index, with timestamp as supporting metadata.
   - Expand recipient wallets up to a configurable maximum depth.
   - Maintain a visited set to prevent cycles and repeated address expansion.
   - Apply configurable limits for maximum nodes, edges, API calls, and time range.
   - Record why traversal stopped (depth limit, no outgoing transfers, duplicate node, request budget, or provider limitation).

4. **Graph persistence layer**
   - Represent wallets as nodes and transfer events as relationships.
   - Use transaction identity fields to avoid accidental duplication.
   - Preserve provenance and retrieval metadata so an investigation can be reproduced.

5. **Risk-indicator layer**
   - Calculate each indicator independently.
   - Define denominators, time windows, normalisation, missing-data handling, and caps explicitly.
   - Return both numeric values and the underlying evidence.
   - Keep the composite score configurable and avoid presenting it as a calibrated probability.

6. **Reporting layer**
   - Present the graph, chronological transfer paths, traversal limits, evidence, indicator contributions, and data-quality warnings.
   - Label the result as an investigative risk signal, not a verdict.

## 9. Upgrade work packages

### WP1 — Correctness and reliability
- Fix optional date handling and make end-date filtering inclusive.
- Normalise wallet-address and transaction-hash comparisons.
- Validate the reference transfer against chain, token contract, sender, recipient, and transaction hash.
- Correct time-window constants and branch ordering.
- Remove division-by-zero paths and use Decimal/integer arithmetic.
- Distinguish empty results from provider errors.
- Add HTTP timeouts, pagination, and explicit retry/rate-limit handling.
- Remove embedded credentials from source code and load secrets from environment configuration.
- Ensure graph persistence failures are surfaced rather than silently followed by risk scoring.

### WP2 — Bounded multi-hop traversal
- Add a traversal service separate from the current one-hop analysis.
- Define depth 0 as the starting wallet; each transfer to a new recipient advances the depth by one.
- Add cycle prevention and per-investigation node, edge, and request budgets.
- Persist each observed transfer once using a stable transfer-event identity.
- Record traversal provenance and stopping conditions.
- Make depth and limits configurable and test them with synthetic graphs.

### WP3 — Explainable risk indicators
- Revisit balance-dominance calculations and explicitly state the balance reconstruction assumptions.
- Define rapid movement windows using correct durations and consistent interval ordering.
- Separate raw outflow, time-weighted outflow, and any retained score so the reported score uses the documented calculation.
- Count transactions and unique wallets separately.
- Correct exchange-interaction evidence to reference the actual outgoing transfer and its hash.
- Maintain a dated, sourced list of known service addresses; unknown or proxy addresses must not be labelled as exchanges without evidence.
- Report component scores and evidence rather than only a single aggregate number.

### WP4 — Testing and reproducibility
- Replace stale tests that target functions no longer present with tests for the current class/service interfaces.
- Add unit tests for date boundaries, address normalisation, token precision, time windows, zero balances, cycles, and depth limits.
- Add integration tests with mocked provider responses.
- Maintain a small set of manually verified transaction fixtures with source, retrieval date, and expected event fields.
- Keep secrets and live provider calls out of routine unit tests.

### WP5 — Evaluation
Use a documented test set containing both synthetic graphs and carefully selected public-chain transfer histories.

Measure:
- **Tracing coverage:** proportion of known downstream transfer events recovered within the declared time range and traversal budget.
- **Path correctness:** whether returned edges and chronological order match the verified event records.
- **Graph expansion:** nodes, edges, and unique wallets discovered by depth.
- **Runtime:** wall-clock processing time under controlled conditions.
- **Provider cost:** number of API requests and rate-limit events.
- **Scoring reproducibility:** whether the same fixed input and configuration produce the same component scores.
- **Explanation completeness:** whether each non-zero score can be linked to explicit transaction evidence and documented rules.

Do not report precision, recall, F1, or fraud-detection accuracy unless a defensible labelled ground-truth dataset and evaluation protocol are available. Synthetic scenarios can test rule behaviour but cannot establish real-world fraud-detection accuracy.

## 10. Experimental design

A suitable initial experiment compares traversal depths (for example, 1, 2, and 3) under the same input wallets, time range, provider, and request budget. Record node count, edge count, verified-event coverage, runtime, and API calls. Repeat with controlled synthetic graphs containing cycles, branching, repeated recipients, and known transfer sequences.

For risk indicators, construct transparent test scenarios that isolate one behaviour at a time (for example, rapid outflow versus slow outflow). Verify that changing one input feature changes only the intended component score, subject to documented dependencies. Report sensitivity to the chosen time windows and weights.

All experiments should record software version, configuration, retrieval date, provider, and dataset/fixture identifiers.

## 11. Expected contributions

The intended contributions are:
1. A reproducible software prototype for bounded, temporal graph exploration of Ethereum USDT transfers.
2. A documented traversal method with explicit expansion controls and provenance.
3. An explainable heuristic framework that exposes its evidence and assumptions.
4. An empirical evaluation of coverage, graph growth, runtime, and request cost under controlled conditions.

These are proposed contributions; their value must be established through implementation and evaluation.

## 12. Risks and limitations

- Blockchain transparency does not reveal the identity or intent of wallet controllers.
- Exchange deposit addresses, custodial wallets, bridges, and intermediaries complicate interpretation.
- A wallet's observed transfer history may be incomplete due to provider limits or selected time windows.
- Heuristic thresholds and weights may be arbitrary until calibrated against suitable evidence.
- Fungible-token flow attribution is not equivalent to tracing uniquely identifiable assets.
- A known-service address list can become stale and may produce false associations.
- A graph path is evidence of transaction connectivity, not proof of common ownership or criminal conduct.

## 13. Suggested implementation sequence

1. Establish a clean baseline and make the existing tests runnable.
2. Fix correctness, security, and ingestion defects.
3. Introduce a canonical transfer-event model and graph persistence identity.
4. Implement bounded multi-hop traversal.
5. Refactor risk indicators and evidence reporting.
6. Build synthetic and verified-chain fixtures.
7. Run and document the evaluation.
8. Update the README, architecture diagram, demo, and research manuscript from measured results.

## 14. JSU positioning

AlphaTrace should be presented as an existing software engineering project that motivates a focused master's research direction. The applicant has independently developed a prototype and now seeks formal research training in graph-based data modelling, blockchain analytics, software engineering methodology, and empirical evaluation.

The project is not presented as a completed academic study or as a validated fraud-detection product. Its current limitations are part of the motivation for the proposed research.

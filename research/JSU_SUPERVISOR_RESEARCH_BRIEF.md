# AlphaTrace — Prospective Master's Research Brief

**Applicant's existing project:** AlphaTrace  
**Proposed field:** Computer Science and Technology / Software Engineering  
**Proposed research title:** *A Graph-Based Framework for Temporal Cryptocurrency Fund-Flow Tracing and Explainable Risk Assessment on Ethereum*

## Background

AlphaTrace is an independently developed prototype for examining suspected USDT ERC-20 fund movements on Ethereum. Its current implementation retrieves token-transfer records through a blockchain data API, filters transactions by time, represents wallet relationships in Neo4j, and applies rule-based indicators relating to balance dominance, rapid outflow, and interaction with a curated set of known exchange addresses.

The existing prototype currently models the initial wallet relationship and direct outgoing transfers from the investigated wallet. It does not yet provide general recursive, multi-hop fund-flow tracing. This limitation motivates the proposed research.

## Research problem

Although public blockchains provide transparent transaction records, investigators must still organise large volumes of transfer events, reconstruct temporal relationships, and examine downstream wallet interactions. A graph representation can make these relationships easier to explore, but unrestricted expansion can become expensive, and heuristic risk scores can be difficult to interpret if their evidence and assumptions are not explicit.

## Proposed aim

To design and evaluate a bounded graph-based framework for tracing downstream USDT transfer relationships on Ethereum and presenting explainable behavioural indicators for investigative analysis.

## Proposed objectives

1. Improve the reliability and correctness of the existing transaction-ingestion and graph-modelling prototype.
2. Implement configurable multi-hop traversal with cycle prevention and explicit resource limits.
3. Model transfer events with temporal and transaction metadata to support reproducible analysis.
4. Refine behavioural heuristics and expose the transaction evidence behind each indicator.
5. Evaluate tracing coverage, graph growth, execution time, API request cost, and score reproducibility using documented test cases.

## Proposed research questions

- How can bounded graph traversal represent downstream USDT fund movements while controlling graph expansion?
- Which transaction-level and temporal features can support transparent behavioural indicators?
- How do traversal depth and resource limits affect coverage, runtime, and data-provider request volume?
- Can the resulting risk assessment provide reproducible explanations tied to observed transaction evidence?

## Proposed methodology

The work will use a design-and-implementation approach followed by controlled empirical evaluation. The prototype will be improved in stages: transaction validation and ingestion reliability; bounded graph traversal; transaction-event persistence; explainable risk indicators; and automated testing. Evaluation will use synthetic transaction graphs for controlled edge cases and a documented set of public Ethereum transfer events for observational testing.

Metrics will include recovered-event coverage against verified fixtures, path correctness, number of nodes and edges, runtime, API request count, and reproducibility of component scores. Fraud-detection accuracy will not be claimed unless a suitable labelled ground-truth dataset is established.

## Existing foundation and applicant preparation

The applicant has a bachelor's degree in Architecture and professional software engineering experience spanning backend systems, fintech, blockchain, automation, and quantitative software. AlphaTrace demonstrates practical experience with Python, blockchain data retrieval, transaction analysis, Django, and Neo4j. The proposed master's research would extend this engineering foundation through formal study of graph data modelling, software engineering methods, and empirical evaluation.

## Scope and limitations

The initial scope is Ethereum Mainnet USDT ERC-20 transfers. The system is intended to support examination of transaction connectivity and behavioural signals; it will not identify wallet owners or establish criminal intent. A graph path is evidence of transaction connectivity, not proof of common ownership or wrongdoing. The project will explicitly document provider limitations, traversal boundaries, heuristic assumptions, and the distinction between observed token transfers and attribution of specific fungible token units.

## Expected outcome

A reproducible research prototype and an empirical report explaining the design, traversal behaviour, indicator calculations, and evaluation results. The work is proposed for development and validation during master's study; no unmeasured performance or detection results are claimed.

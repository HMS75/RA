# Literature review: methods for reducing LLM hallucination

## Overview  
Hallucination in large language models (LLMs) is when the model produces content that is factually incorrect, unfaithful to the input, or unaligned with user instructions. The phenomenon is divided into intrinsic hallucinations, which contradict source content, and extrinsic hallucinations, which are unverifiable with the source [1]. Researchers have found that hallucinations often arise when a model tries to stay fluent while it is uncertain about factual content [1].

## Main approaches  
**Detection** – External verification methods use knowledge bases or search engines, but they are limited by the coverage and timeliness of those sources [1]. Consistency‑based methods, such as self‑consistency checking, evaluate whether multiple generations agree with each other [1]. The HalluScan benchmark evaluates six detection methods across 72 configurations, finding that Self‑Evaluation achieves the highest AUROC (0.688) and Self‑Consistency achieves 0.638, while some methods show score‑direction inversion [2].  
**Mitigation** – Adjusting internal model components, such as attention heads or specific neurons, can improve truthfulness but may introduce side effects [3]. Control codes added during training and decoding guide the model toward lexical precision and entailment, reducing hallucinations in knowledge‑grounded dialogue [4]. Memory‑augmented models can be constrained by scaling the readout vector, which mitigates hallucinations in a training‑free way and outperforms state‑of‑the‑art editing methods on Wikipedia‑style biographies [5]. Prompt‑based strategies, including self‑monitoring prompts and Self‑Familiarity, use prompt engineering to predict and avoid hallucinations before they are generated [6].

## How the papers compare  
- HalluScan provides a systematic benchmark that quantifies detection performance and cost savings, showing that Adaptive Detection Routing reduces cost by ~1.7× with minimal quality loss [2].  
- External verification methods are more reliable when the knowledge base is up‑to‑date, whereas consistency methods are cheaper but less accurate on some domains [1][2].  
- Internal manipulation (attention or neuron tuning) can improve factuality but may affect other safety properties, such as resistance to jailbreaking [3].  
- Control codes and prompt‑based methods operate at inference time without retraining, but they can reduce generation fluency and diversity [4][6].  
- Memory‑augmented constraints are a training‑free alternative that shows strong results on specific tasks (biographical entries) but have not been evaluated across many domains [5].

## Limitations and open problems  
Evidence shows that many mitigation techniques overlook potential side effects or safety trade‑offs, such as increased jailbreaking vulnerability [3]. Benchmarks often focus on isolated tasks or single datasets, providing limited insight into how hallucinations emerge across the entire LLM lifecycle [9]. Some detection methods perform poorly on certain domains or exhibit score‑direction inversion, indicating that effectiveness varies with context [2]. Log‑probability‑based detection can reduce hallucination rates substantially in finance QA, but its performance relative to other benchmarks is still unclear [8]. The field lacks unified evaluation protocols and shared test sets, making direct comparison difficult [10].

## Gaps in the evidence  
There is weak evidence that a single mitigation approach consistently outperforms others across all domains, because most studies evaluate on a narrow set of tasks or models [2][5][6]. The interaction between hallucination mitigation and other safety objectives (e.g., jailbreak resistance, privacy) remains underexplored [3]. Few works provide long‑term, lifecycle‑oriented studies that trace how upstream training choices influence downstream hallucination behavior [9]. Consequently, more comprehensive, standardized benchmarks and systematic analyses of trade‑offs are needed to advance reliable LLM deployment.

## Paper comparison

| Paper | Method | Data / benchmarks | Key results | Limitations |
|---|---|---|---|---|
| Hallucinations in LLMs: A Lifecycle-Based Survey of Causes, Detection, Mitigation, and Prevention (2026) | Lifecycle-based survey using systematic literature identification, screening, PRISMA flow, coding, and comparative analysis. | Benchmarks include NQ, TriviaQA, WebQuestions, CuratedTrec, FEVER; metrics like EM, AUC, accuracy reported. | Provides three-fold categorization, standardized framework, detection/mitigation strategies, and comparative effectiveness of interventions. | Not explicitly stated; reliance on available benchmarks, data quality, and evaluation scope limited to outputs. |
| HalluScan: A Systematic Benchmark for Detecting and Mitigating Hallucinations in Instruction-Following LLMs (2026) | HalluScan benchmark evaluates 6 detection methods across 4 models, 3 domains, 72 configs. | 600 responses (50 Q per domain ×4 models), 3 domains, 72 configurations. | Hallucination metric HalluScore r=0.41; ADR cuts cost 2×, AUROC loss 0.1%; NLI Verif AUROC 0.88; Self‑Eval 0.688. | not stated |
| Detecting AI Hallucinations in Finance: An Information-Theoretic Method Cuts Hallucination Rate by 92% (2025) | ECLIPSE matches semantic entropy to evidence capacity using entropy estimation and perplexity decomposition. | 200 balanced financial QA samples from SEC filings and transcripts, GPT-3.5-turbo used. | ROC AUC 0.89, average precision 0.90, 92% hallucination reduction over baseline. | Validated only on synthetic data; no natural hallucinations; logprob dependency; adversarial robustness untested. |
| A Systematic Literature Review of Code Hallucinations in LLMs: Characterization, Mitigation Methods, Challenges, and Future Directions for Reliable AI (2025) | Systematic review of 60 papers per Kitchenham, using defined search terms, addressing four research questions. | Benchmarks include static metrics and dynamic checks like compilation and execution correctness. | Identified causes, mitigation strategies (knowledge-enhanced, constrained decoding, post-editing), code challenges, and evaluation methods. | Need unified hallucination-aware benchmarks; challenges in private codebases; balancing generalization and factual reliability. |
| Hallucination by Code Generation LLMs: Taxonomy, Benchmarks, Mitigation, and Challenges (2025) | Survey reviews studies, classifies hallucination types, examines benchmarks, mitigation techniques, and highlights challenges. | Reviewed existing benchmarks for code hallucination detection. | Identified hallucination categories, evaluated benchmarks, assessed mitigation methods, and outlined future research directions. | not stated |

## Sources

[1] Counterfactual Probing for Hallucination Detection and Mitigation in Large Language Models (2025), section: Related Work - https://arxiv.org/abs/2508.01862v1
[2] HalluScan: A Systematic Benchmark for Detecting and Mitigating Hallucinations in Instruction-Following LLMs (2026), section: Abstract - https://arxiv.org/abs/2605.02443v2
[3] The Unintended Trade-off of AI Alignment:Balancing Hallucination Mitigation and Safety in LLMs (2025), section: Introduction - https://arxiv.org/abs/2510.07775v2
[4] Hallucination Detection and Hallucination Mitigation: An Investigation (2024), section: Methods - https://arxiv.org/abs/2401.08358v1
[5] Generation Constraint Scaling Can Mitigate Hallucination (2024), section: Abstract - https://arxiv.org/abs/2407.16908v1
[6] Insights into Classifying and Mitigating LLMs' Hallucinations (2023), section: Methods - https://arxiv.org/abs/2311.08117v1
[8] Detecting AI Hallucinations in Finance: An Information-Theoretic Method Cuts Hallucination Rate by 92% (2025), section: Discussion - https://arxiv.org/abs/2512.03107v1
[9] Hallucinations in LLMs: A Lifecycle-Based Survey of Causes, Detection, Mitigation, and Prevention (2026), section: Limitations - https://arxiv.org/abs/2608.26168v1
[10] Detecting AI Hallucinations in Finance: An Information-Theoretic Method Cuts Hallucination Rate by 92% (2025), section: Limitations - https://arxiv.org/abs/2512.03107v1

## Warnings

- No citation: Hallucination in large language models (LLMs) is when the model produces content that is factually incorrect, unfaithful
- No citation: Consequently, more comprehensive, standardized benchmarks and systematic analyses of trade‑offs are needed to advance re
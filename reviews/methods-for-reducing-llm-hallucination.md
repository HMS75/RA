# Literature review: methods for reducing LLM hallucination

## Overview  
Large language models (LLMs) often produce factually incorrect or inconsistent content, known as hallucination, which harms their reliability in real‑world tasks [5].  
Studies have concentrated on detecting when hallucinations occur and on mitigating them once identified [3].  
Recent work shows that active detection and mitigation can substantially lower hallucination rates, for example reducing GPT‑3.5 hallucinations from 47.5 % to 14.5 % on average [1][5].  
The approaches differ in whether they operate at inference time, during training, or by augmenting the model’s knowledge base [1][2][4].  

## Main approaches  

- **Detection by confidence or semantic consistency**: Methods analyze model log probabilities, entropy, or linear probing to flag low‑confidence or inconsistent tokens. These techniques achieve high recall and can be deployed at inference time [3].  

- **Mitigation through internal model changes**: Strategies such as adjusting attention heads, identifying neurons that promote truthfulness, or scaling memory readout vectors constrain generation and reduce hallucinations [3][2].  

- **Knowledge‑grounding and retrieval‑augmented generation**: Models fuse external knowledge graphs or retrieval systems with dialogue history to ground responses in factual data [4][18].  

- **Control codes and contrastive learning**: Introducing explicit control tokens or contrastive objectives guides generation toward truthful outputs [4].  

- **Self‑refinement and phase‑wise self‑reward**: Models iteratively refine outputs or reward internally generated hallucination scores, trading inference cost for reduced hallucination severity [11][7][9].  

## How the papers compare  

- The active detection–mitigation pipeline reported in one study achieves a recall of ~88 % and mitigates 57.6 % of detected hallucinations, cutting overall hallucination rates to 14.5 % for GPT‑3.5 [5].  
- A memory‑augmented decoding method that scales the readout vector shows training‑free mitigation and outperforms state‑of‑the‑art editing methods on Wikipedia‑style biographies [2].  
- The RHO dialogue model merges knowledge‑graph triples with dialogue history, using local and global grounding to align responses, illustrating a knowledge‑grounded approach [4].  
- Retrieval‑augmented generation (Rowen) outperforms baselines on TruthfulQA and StrategyQA, indicating strong generalization to new datasets and models [10].  
- Self‑refinement consistently reduces hallucinations more than retrieval‑augmented generation, but the gains are modest and retrieval quality remains a limiting factor [11].  
- Phase‑wise self‑reward (PSRD) shows a clear trade‑off: lower thresholds decrease inference time but increase hallucination severity, with a 67.2 % CHAIR reduction at a 30 % threshold [7][9].  

## Limitations and open problems  

- Many mitigation methods are **corrective** rather than preventive; they do not eliminate underlying causes of hallucination and may rely on additional infrastructure such as retrieval systems or verification pipelines [8].  
- Interventions that modify internal representations can introduce side effects or fail to generalize across tasks, and their safety impact has not been fully explored [3].  
- Computational cost varies widely: some methods require multiple decoding branches or additional inference time, limiting real‑time deployment [7][9][11].  
- Benchmarks often focus on isolated outputs and lack lifecycle‑wide evaluation, so the full impact of mitigation across the generation pipeline remains unclear [8][16].  
- Knowledge‑grounding approaches depend heavily on the quality and coverage of external resources, and retrieval errors can limit effectiveness [4][10].  

## Gaps in the evidence  

- Lifecycle‑oriented benchmarks that trace hallucination emergence across data collection, training, and inference stages are still scarce [8][16].  
- Empirical studies on preventive strategies that reduce hallucination before generation start are limited [8][3].  
- Comparative analyses across diverse domains (e.g., code generation, dialogue, summarization) are incomplete, especially for multimodal models [7][11][10].  
- The trade‑offs between effectiveness, efficiency, and safety of mitigation techniques need systematic quantification [7][8][11].  
- More research is needed on how mitigation affects downstream tasks such as decision support or code synthesis [11].

## Paper comparison

| Paper | Method | Data / benchmarks | Key results | Limitations |
|---|---|---|---|---|
| A Systematic Literature Review of Code Hallucinations in LLMs: Characterization, Mitigation Methods, Challenges, and Future Directions for Reliable AI (2025) | Conducted systematic literature review per Kitchenham guidelines, surveying 60 papers. | Benchmarks include static metrics and dynamic checks like compilation and execution correctness. | Identified causes: data noise, exposure bias, semantic grounding; mitigation: knowledge-enhanced, constrained, post-editing; code-specific challenges: syntax, typing, libraries; detection via program analysis, symbolic execution, unit testing. | Need unified, hallucination-aware benchmarks; challenges balancing generalization and factual reliability; detection in private codebases. |
| A Stitch in Time Saves Nine: Detecting and Mitigating Hallucinations of LLMs by Validating Low-Confidence Generation (2023) | Actively detect hallucinations using logit uncertainty, validate via queries, then mitigate by repairing sentences before continuing generation. | GPT-3.5 (text‑davinci‑003) article generation, multi‑hop/false premise questions, and Vicuna LLM. | Recall 88% detection; mitigation fixes 57.6% of detected cases; hallucinations drop from 47.5% to 14.5%. | not stated |
| Mitigating Multimodal Hallucination via Phase-wise Self-reward (2026) | Introduce Phase-wise Self-Reward Decoding (PSRD) that distills a lightweight reward model to guide online decoding and suppress hallucinations. | Evaluated on AMBER, Object HalBench, MMHal-Bench, POPE, AMBER HalDet, and MHal-detect. | PSRD cuts hallucination rate of LLaVA-1.5-7B by 50%, outperforms post-hoc methods on five benchmarks, and balances performance with inference efficiency. | not stated |
| Hallucinations in LLMs: A Lifecycle-Based Survey of Causes, Detection, Mitigation, and Prevention (2026) | Structured survey using systematic literature review and lifecycle-based coding of hallucination causes and mitigations. | Benchmarks include NQ, TriviaQA, WebQuestions, FEVER, BioGEN, LongFact, FollowRAG, etc. | Identified data, training, inference causes; mapped detection, mitigation, prevention techniques; compared benchmark effectiveness. | Limitations include data bias, retrieval dependence, limited generalization, human bias, high cost, domain specificity, knowledge forgetting. |
| Hallucination by Code Generation LLMs: Taxonomy, Benchmarks, Mitigation, and Challenges (2025) | Survey: classify hallucination types, review benchmarks/mitigation, identify challenges, propose research directions. | Existing benchmarks reviewed, but specific ones not listed. | Taxonomy of hallucinations, benchmark review, mitigation strategies, challenges, future research roadmap. | not stated |

## Sources

[1] A Stitch in Time Saves Nine: Detecting and Mitigating Hallucinations of LLMs by Validating Low-Confidence Generation (2023), section: Conclusion - https://arxiv.org/abs/2307.03987v2
[2] Generation Constraint Scaling Can Mitigate Hallucination (2024), section: Abstract - https://arxiv.org/abs/2407.16908v1
[3] The Unintended Trade-off of AI Alignment:Balancing Hallucination Mitigation and Safety in LLMs (2025), section: Introduction - https://arxiv.org/abs/2510.07775v2
[4] Hallucination Detection and Hallucination Mitigation: An Investigation (2024), section: Methods - https://arxiv.org/abs/2401.08358v1
[5] A Stitch in Time Saves Nine: Detecting and Mitigating Hallucinations of LLMs by Validating Low-Confidence Generation (2023), section: Abstract - https://arxiv.org/abs/2307.03987v2
[7] Mitigating Multimodal Hallucination via Phase-wise Self-reward (2026), section: Methods - https://arxiv.org/abs/2604.17982v1
[8] Hallucinations in LLMs: A Lifecycle-Based Survey of Causes, Detection, Mitigation, and Prevention (2026), section: Methods - https://arxiv.org/abs/2608.26168v1
[9] Mitigating Multimodal Hallucination via Phase-wise Self-reward (2026), section: Methods - https://arxiv.org/abs/2604.17982v1
[10] Rowen: Adaptive Retrieval-Augmented Generation for Hallucination Mitigation in LLMs (2024), section: Results - https://arxiv.org/abs/2402.10612v3
[11] When LLMs Invent Rust Crates: An Empirical Study of Hallucination Patterns and Mitigation (2026), section: Results - https://arxiv.org/abs/2606.08444v2
[16] Hallucinations in LLMs: A Lifecycle-Based Survey of Causes, Detection, Mitigation, and Prevention (2026), section: Limitations - https://arxiv.org/abs/2608.26168v1
[18] A Systematic Literature Review of Code Hallucinations in LLMs: Characterization, Mitigation Methods, Challenges, and Future Directions for Reliable AI (2025), section: Methods - https://arxiv.org/abs/2511.00776v1

## Warnings

- No citation: - **Detection by confidence or semantic consistency**: Methods analyze model log probabilities, entropy, or linear probi
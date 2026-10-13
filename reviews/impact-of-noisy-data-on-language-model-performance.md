# Literature review: impact of noisy data on language model performance

## Overview  
Language models trained on corpora with conflicting or low‑quality content often generate outputs that do not align with any part of the training data, producing both extrinsic and intrinsic hallucinations. This phenomenon is a direct consequence of noisy or contradictory data in the training set.  
- Contradictory or noisy training data can confuse semantic understanding and parametric knowledge learning, leading to hallucinations [10].  
- Hallucinations are considered a form of generalization error, arising when a model’s predictions deviate from the ground‑truth function due to imperfect data or training conditions [3].  

## Main approaches  
### Data‑level mitigation  
- Retrieval‑augmented generation (RAG) incorporates external knowledge at generation time to ground outputs and reduce hallucinations caused by data noise [8].  
- Post‑training data augmentation and cleaning of low‑quality or uncurated corpora are used to improve factual grounding [7][8].  

### Training‑level mitigation  
- Model editing and contrastive learning are applied during fine‑tuning to separate factual from spurious patterns learned from noisy data [8].  
- Reinforcement learning with human or AI feedback (RLHF) is employed to shape model behaviour toward truthfulness, though it can also introduce trade‑offs with safety and factual accuracy [6][8].  

### Inference‑time mitigation  
- Self‑reflection and confidence‑calibration modules can flag uncertain generations, reducing the risk of confident hallucinations that arise from noisy data [8][2].  
- External fact‑checking pipelines are used at generation time to verify the factuality of outputs before they are returned to the user [8].  

### Regularization techniques  
- Temperature scaling, a post‑hoc calibration method, has been shown to improve Expected Calibration Error (ECE) for models, providing a more reliable uncertainty signal that can mitigate hallucinations stemming from noisy training signals [2].  

## How the papers compare  
| Lifecycle stage | Typical methods | Reported impact on hallucination | Key source |
|-----------------|-----------------|-----------------------------------|------------|
| Data | RAG, data cleaning | Improves factual grounding, reduces extrinsic hallucinations | [8] |
| Training | Model editing, contrastive learning, RLHF | Alters internal representations, can reduce both hallucination and safety failures | [8][6] |
| Inference | Self‑reflection, confidence calibration, external fact‑checking | Provides real‑time safeguards, often used as last‑line defense | [8] |
| Calibration | Temperature scaling | Lowers ECE, improves uncertainty estimates | [2] |

The papers emphasize data‑level fixes as the most direct response to noisy training material, whereas training‑ and inference‑time techniques act as complementary safeguards. Calibration methods are applied across stages to improve the reliability of model confidence.  

## Limitations and open problems  
- Many mitigation studies rely on auxiliary systems (retrieval, fact‑checking) that introduce additional infrastructure costs and potential new failure modes [8].  
- The trade‑off between reducing hallucinations and maintaining factual accuracy or safety remains poorly quantified; some interventions that improve truthfulness may inadvertently increase refusal or safety errors [6].  
- Calibration improvements measured by ECE do not guarantee factual correctness, as high confidence can still coincide with hallucinations [5][2].  
- Existing benchmarks (HalluLens, HalluScan, OpenHalDet) evaluate hallucination rates but rarely isolate the effect of noisy versus clean training data, limiting causal conclusions about noise impact [14][13][15].  

## Gaps in the evidence  
- The influence of noisy training data on core performance metrics—accuracy, calibration, and generalization—has limited empirical support; most studies report qualitative or anecdotal findings rather than quantitative benchmarks [10].  
- Effectiveness of specific data‑cleaning or robust regularization strategies against noise is not systematically compared across models or datasets [7][8].  
- Benchmark protocols that dynamically generate test questions and evaluate refusal or abstention are relatively recent and have not yet been standardized for noisy‑data evaluation [14].  
- Cross‑lingual generalizability of noise mitigation techniques remains unexplored, as current studies focus primarily on English datasets and models [13].  

These gaps highlight the need for controlled experiments that systematically vary training‑data noise levels and evaluate corresponding changes in accuracy, calibration, and generalization across diverse benchmark settings.

## Paper comparison

| Paper | Method | Data / benchmarks | Key results | Limitations |
|---|---|---|---|---|
| A Systematic Literature Review of Code Hallucinations in LLMs: Characterization, Mitigation Methods, Challenges, and Future Directions for Reliable AI (2025) | Systematic literature review of 60 papers, following Kitchenham guidelines, categorizing causes, mitigation, and evaluation. | Benchmarks include static metrics and dynamic checks such as compilation and execution correctness. | Hallucinations arise from data noise, exposure bias, semantic gaps; mitigated by knowledge‑enhanced decoding, constrained generation, post‑editing; code challenges include syntax, typing, libraries. | Few code‑hallucination studies; benchmarks lack unified, hallucination‑aware metrics; challenges in private codebases and balancing reliability with generalization. |
| Theoretical Foundations and Mitigation of Hallucination in Large Language Models (2025) | Formal definitions, risk bounds via PAC-Bayes and Rademacher, detection (uncertainty, calibration, attention) and mitigation (retrieval, fine-tuning, logit, verification). | Recommended datasets, metrics, setups are proposed, but specific names are not provided. | Derived theoretical risk bounds, surveyed detection/mitigation strategies, proposed unified workflow and evaluation guidelines. | not stated |
| HalluLens: LLM Hallucination Benchmark (2025) | Proposed HalluLens benchmark with a clear hallucination taxonomy, new extrinsic tasks, dynamic test generation, and analysis of existing benchmarks. | HalluLens comprising three new extrinsic hallucination tasks and three existing intrinsic tasks, with dynamic test set generation. | Benchmark evaluates extrinsic hallucinations, resists data leakage, and offers comprehensive analysis separating hallucination from factuality. | not stated |
| Hallucinations in LLMs: A Lifecycle-Based Survey of Causes, Detection, Mitigation, and Prevention (2026) | Lifecycle‑based survey: systematic literature review, PRISMA flow, coding, comparative analysis of hallucination causes, detection, mitigation, prevention. | Benchmarks cited: NQ, TriviaQA, WebQuestions, CuratedTrec, FEVER; methods evaluated on EM, AUC, accuracy metrics. | Lifecycle perspective shows hallucinations stem from data, training, inference; mitigation via data curation, model editing, self‑reflection; comparative effectiveness reported. | Benchmarks focus on outputs, not full lifecycle; methods limited by retrieval bias, data quality, memory, human/AI bias, scalability constraints. |
| HalluScan: A Systematic Benchmark for Detecting and Mitigating Hallucinations in Instruction-Following LLMs (2026) | Systematic benchmark evaluating hallucination detection across 6 methods, 4 model families, 3 domains. | 600 responses from 4 open-weight LLMs across 3 domains, 72 configs. | Self-Evaluation AUROC 0.688; ADR cuts cost 2×, AUROC drop 0.1%; HalluScore correlates r=0.41. | HalluScore shows weak correlation with quality, requires score-direction correction, and needs domain-specific thresholds. |

## Sources

[2] Weakly Supervised Distillation of Hallucination Signals into Transformer Representations (2026), section: Methods - https://arxiv.org/abs/2604.06277v1
[3] Theoretical Foundations and Mitigation of Hallucination in Large Language Models (2025), section: Introduction - https://arxiv.org/abs/2507.22915v1
[5] A Systematic Literature Review of Code Hallucinations in LLMs: Characterization, Mitigation Methods, Challenges, and Future Directions for Reliable AI (2025), section: Methods - https://arxiv.org/abs/2511.00776v1
[6] The Unintended Trade-off of AI Alignment:Balancing Hallucination Mitigation and Safety in LLMs (2025), section: Introduction - https://arxiv.org/abs/2510.07775v2
[7] Hallucinations in LLMs: A Lifecycle-Based Survey of Causes, Detection, Mitigation, and Prevention (2026), section: Methods - https://arxiv.org/abs/2608.26168v1
[8] Hallucinations in LLMs: A Lifecycle-Based Survey of Causes, Detection, Mitigation, and Prevention (2026), section: Methods - https://arxiv.org/abs/2608.26168v1
[10] HalluLens: LLM Hallucination Benchmark (2025), section: Introduction - https://arxiv.org/abs/2504.17550v1
[13] HalluScan: A Systematic Benchmark for Detecting and Mitigating Hallucinations in Instruction-Following LLMs (2026), section: Limitations - https://arxiv.org/abs/2605.02443v2
[14] HalluLens: LLM Hallucination Benchmark (2025), section: Introduction - https://arxiv.org/abs/2504.17550v1
[15] OpenHalDet: A Unified Benchmark for Hallucination Detection across Diverse Generation Scenarios (2026), section: Introduction - https://arxiv.org/abs/2606.06959v1

## Warnings

- No citation: Language models trained on corpora with conflicting or low‑quality content often generate outputs that do not align with
- No citation: This phenomenon is a direct consequence of noisy or contradictory data in the training set.
- No citation: | Lifecycle stage | Typical methods | Reported impact on hallucination | Key source |
- No citation: |-----------------|-----------------|-----------------------------------|------------|
- No citation: The papers emphasize data‑level fixes as the most direct response to noisy training material, whereas training‑ and infe
- No citation: Calibration methods are applied across stages to improve the reliability of model confidence.
- No citation: These gaps highlight the need for controlled experiments that systematically vary training‑data noise levels and evaluat
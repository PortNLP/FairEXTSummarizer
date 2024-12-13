# Fair Summarization: Bridging Quality and Diversity in Extractive Summaries

This repository contains the resources and related materials for the paper:

**Fair Summarization: Bridging Quality and Diversity in Extractive Summaries**  
*Sina Bagheri Nezhad, Sayan Bandyapadhyay, Ameeta Agrawal*  
Published on arXiv: [arXiv:2411.07521](https://arxiv.org/abs/2411.07521)  
Presented at the **Algorithmic Fairness through the Lens of Metrics and Evaluation Workshop**  
at The 38th Conference on Neural Information Processing Systems (NeurIPS 2024), Vancouver, Canada.  

---

## Overview

**Fair Summarization** addresses the critical challenge of ensuring **fairness** and **quality** in multi-document summarization of user-generated content, such as social media posts. Existing methods often fail to ensure equitable representation across social groups, leading to biased and unbalanced summaries.

We propose two novel fairness-aware extractive summarization methods:

1. **FairExtract**: A clustering-based approach that ensures group representation balance.
2. **FairGPT**: A GPT-3.5-turbo based method incorporating fairness constraints.

We evaluate these methods using the DivSumm dataset, which contains dialect-diverse tweets, and demonstrate their ability to achieve fairness while maintaining high-quality summaries.

---

## Key Features

- **FairExtract**: Ensures diversity using fair clustering and proportional group representation.
- **FairGPT**: Incorporates fairness constraints using LLMs with extractive summarization.
- **Evaluation Metrics**: Novel composite metrics combining **quality** (SUPERT, BLANC, SummaQA, etc.) and **fairness**.
- **Trade-off Analysis**: Insights into the balance between fairness and summary quality.

---

## Dataset

We evaluate our methods on the **DivSumm** dataset:
- **Content**: Tweets from three social groups – White-aligned, Hispanic, and African-American dialects.
- **Topics**: 25 diverse topics, 30 tweets per group.
- **Group Pairings**: Experiments focus on balancing pairwise combinations (White-Hispanic, Hispanic-African American, White-African American).
- **Access**: The dataset is available at the [DivSumm GitHub Repository](https://github.com/PortNLP/DivSumm).

---

## Methods

### FairExtract: A Clustering-based Approach

1. **Fairlet Decomposition**: Ensures balanced representation at the smallest level of grouping.
2. **Clustering**: Applies k-median clustering on fairlet centers to form diversity-aware clusters.
3. **Summary Selection**: Constructs a final extractive summary by selecting representatives from each fairlet.

### FairGPT: A Fairness-Constrained LLM Approach

1. **Input Preparation**: Divides input documents into group-labeled subsets.
2. **Summarization with GPT-3.5**: Ensures equal sentence selection from each group using fairness constraints.
3. **Longest Common Subsequence (LCS)**: Matches generated outputs with the original input sentences to ensure fidelity.

---

## Evaluation

We use reference-free quality and fairness metrics to evaluate our methods:
- **SUPERT**
- **BLANC**
- **SummaQA**
- **BARTScore**
- **UniEval**
- **Fairness Metric (F)**: Representation gap transformed to align with quality metrics.

We introduce **composite metrics** (e.g., SUPERT+F, BLANC+F) that integrate fairness and quality into a single evaluation framework.

---

## Results

### Key Findings:
- **FairGPT** achieves the best balance between fairness and quality.
- **FairExtract** excels among clustering-based methods, maintaining diversity without significant quality loss.
- Composite metrics demonstrate the effectiveness of our methods in achieving fairness-aware summarization.

### Composite Metrics Table

| Model                  | SUPERT+F | BLANC+F | SumQA+F | BARTSc+F | UniEval+F |
|------------------------|----------|---------|---------|----------|-----------|
| **Clustering-based Methods** |          |         |         |          |           |
| 	exttt{Naive}         | 0.585    | 0.609   | 0.468   | 0.713    | 0.601     |
| 	exttt{NaiveFair}     | 0.720    | 0.749   | 0.606   | **0.848**| 0.732     |
| 	exttt{TextRank Vanilla} | 0.585    | 0.531   | 0.494   | 0.703    | 0.605     |
| 	exttt{TextRank Cluster-A} | 0.571    | 0.513   | 0.467   | 0.689    | 0.577     |
| 	exttt{TextRank Cluster-H} | 0.579    | 0.521   | 0.478   | 0.687    | 0.588     |
| 	exttt{BERT-EXT Vanilla} | 0.582    | 0.590   | 0.453   | 0.725    | 0.578     |
| 	exttt{BERT-EXT Cluster-A} | 0.616    | 0.615   | 0.479   | 0.737    | 0.604     |
| 	exttt{BERT-EXT Cluster-H} | 0.598    | 0.583   | 0.457   | 0.723    | 0.564     |
| **FairExtract (Ours)** | **0.724** | **0.758**| **0.607**| 0.845    | **0.747** |
| **LLM-based Methods** |          |         |         |          |           |
| 	exttt{ChatGPT-EXT}   | 0.737    | 0.607   | 0.454   | 0.817    | 0.611     |
| **FairGPT (Ours)**     | **0.837**| **0.760**| **0.615**| **0.945**| **0.751** |

*Table: Evaluation results using composite metrics for clustering-based and LLM-based summarization methods. The best values for each metric are highlighted in bold.*

---

## Citation

If you use this work, please cite our paper:

```bibtex
@misc{nezhad2024fairsummarizationbridgingquality,
      title={Fair Summarization: Bridging Quality and Diversity in Extractive Summaries}, 
      author={Sina Bagheri Nezhad and Sayan Bandyapadhyay and Ameeta Agrawal},
      year={2024},
      eprint={2411.07521},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2411.07521}, 
}
```

---

## Authors
- **Sina Bagheri Nezhad**
- **Sayan Bandyapadhyay**
- **Ameeta Agrawal**

---

## Acknowledgments

This work was supported by the National Science Foundation under Grant No. AF 2311397 and CRII:RI 2246174.

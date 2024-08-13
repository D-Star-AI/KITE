# KITE
KITE (Knowledge-Intensive Task Evaluation) is an end-to-end benchmark for RAG pipelines.

While retrieval augmented generation (RAG) can be thought of as just an extension of information retrieval (IR), the problem is different enough that existing IR benchmarks are quite limiting when applied to RAG. IR benchmarks, like BEIR, just evaluate relevance rankings of documents. While this is a good way to evaluate embeddings and rerankers, there's more to RAG than that. The only way to truly evaluate complete RAG systems is with an end-to-end evaluation, where the benchmark provides a corpus of documents to index and a set of questions with ground truth answers and grading rubrics. Then you use a strong LLM to grade the model output. That's what KITE does.

## Datasets
KITE currently consists of 4 datasets and a total of 50 questions.
- **AI Papers** - ~100 academic papers about AI and RAG, downloaded from arXiv in PDF form.
- **BVP Cloud 10-Ks** - 10-Ks for all companies in the Bessemer Cloud Index (~70 of them), in PDF form.
- **Sourcegraph Company Handbook** - ~800 markdown files, with their original directory structure, downloaded from Sourcegraph's publicly accessible company handbook GitHub [page](https://github.com/sourcegraph/handbook/tree/main/content).
- **Supreme Court Opinions** - All Supreme Court opinions from Term Year 2022 (delivered from January '23 to June '23), downloaded from the official Supreme Court [website](https://www.supremecourt.gov/opinions/slipopinion/22) in PDF form.

The documents are contained in the `knowledge-base-contents` folder.

The queries are contained in json files in the `queries` folder. Each sample contains the keys `query`, `gt_answer`, and `rubric`.

## Sample generation process
Most of the samples were written by hand, but some were generated using an LLM (`Claude 3.5 Sonnet`) and then reviewed manually. For the LLM-generated samples, an entire document (limited to 100k characters) was provided as context, and the LLM was prompted to generate 5 challenging questions, along with correct answers and grading rubrics. 

More than 50 samples were created initially. They were filtered down by running a strong baseline RAG system (Top-20 retrieval with Cohere reranker) on them and then throwing away some of the easier questions so that the baseline score is below 50%.

## Grading
Grading is done with a strong LLM (`GPT-4o` is used by default). The LLM is given the model answer, the ground truth answer, and the grading rubric, and is prompted to output a grade on a scale of 0-10.

## Results
Full model output and grades are included for a few different RAG configurations in the `results` folder. We tested the following configurations using [dsRAG](https://github.com/D-Star-AI/dsRAG):
- Top-k retrieval (baseline)
- Relevant segment extraction (RSE)
- Top-k retrieval with contextual chunk headers (CCH)
- CCH+RSE

Cohere English embeddings and the Cohere 3 English reranker were used for all configurations. LLM responses were generated with GPT-4o, and grading was also done with GPT-4o.

|                         | top_k    | rse    | cch_top_k    | cch_rse    |
|-------------------------|----------|--------|--------------|------------|
| AI Papers               | 4.5      | 7.9    | 4.7          | 7.9        |
| BVP Cloud               | 2.6      | 4.4    | 6.3          | 7.8        |
| Sourcegraph             | 5.7      | 6.6    | 5.8          | 9.4        |
| Supreme Court Opinions  | 6.1      | 8.0    | 7.4          | 8.5        |
| Average                 | 4.72     | 6.73   | 6.04         | 8.42       |

Using contextual chunk headers and RSE together leads to a dramatic improvement in performance, from 4.72 -> 8.42. For more information on CCH and RSE, you can check out this [article](https://d-star.ai/solving-the-out-of-context-chunk-problem-for-rag) or the [dsRAG](https://github.com/D-Star-AI/dsRAG) repo.

## Limitations
- English-only
- With only 50 samples, small tweaks won't produce statistically significant results.

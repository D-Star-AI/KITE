import os
import json
from openai import OpenAI
client = OpenAI()

EVALUATION_PROMPT = """
Your job is to evaluate the performance of an AI-powered question answering system. You will be given a query, a ground truth answer, and the answer given by the AI. Your task is to grade the AI's answer on a scale of 0-10. A score of 0 means the AI's answer is wrong. A score of 10 means the AI's answer is completely correct.

Your response must ONLY be an integer between 0 and 10 (inclusive). Do not include any other text in your response.

GUIDELINES FOR GRADING
- The ground truth answers are often lacking in detail, so if the AI's answer is more detailed than the ground truth answer, then that's generally a good sign.
- Be wary of overly broad or general AI answers. If the AI's answer lacks specifics, then it probably isn't a good answer.
- If a grading rubric is included in the GRADING RUBRIC section, then pay close attention to it. The rubric will tell you specific things to look for in the AI's answer.
- Maintain high standards when grading. A score of 10 should be reserved for answers that are nearly perfect. Answers that miss key details or don't fully answer the question should be heavily penalized.

QUERY
{query}

GROUND TRUTH ANSWER
{ground_truth_answer}

GRADING RUBRIC
{rubric}

AI-GENERATED ANSWER
{model_answer}

GRADE
""".strip()

# we'll use this to run the evaluation prompt
def openai_api_call(chat_messages: list[dict], model_name: str = "gpt-4o-2024-08-06", max_tokens: int = 1) -> str:
    client.api_key = os.getenv("OPENAI_API_KEY")
    response = client.chat.completions.create(
        model=model_name,
        messages=chat_messages,
        max_tokens=max_tokens,
        temperature=0.0,
    )
    llm_output = response.choices[0].message.content.strip()
    return llm_output

# evaluate the model's predictions against the ground truth answers
def evaluate_response(query, gt_answer, rubric, model_answer):
    prompt = EVALUATION_PROMPT.format(query=query, ground_truth_answer=gt_answer, rubric=rubric, model_answer=model_answer)
    chat_messages = [{"role": "user", "content": prompt}]
    response = openai_api_call(chat_messages, model_name="gpt-4o-2024-08-06", max_tokens=1)
    return response

def run_evaluation(eval_set: list[dict], test_set_name: str, config_name: str):
    """
    - eval_set is a list of dictionaries, where each dictionary contains:
        - "query": the query
        - "gt_answer": the ground truth answer, i.e. what you want the model to output
        - "rubric": additional notes for the evaluator
        - "response": the model's response to the query
    """
    # run the evaluation
    eval_results = []
    for eval_item in eval_set:
        query = eval_item["query"]
        gt_answer = eval_item["gt_answer"]
        rubric = eval_item["rubric"]
        model_answer = eval_item["response"]

        grade = evaluate_response(query, gt_answer, rubric, model_answer)
        print (query)
        print (grade)
        print ("")

        # save the results
        eval_results.append({
            "query": query,
            "gt_answer": gt_answer,
            "rubric": rubric,
            "model_answer": model_answer,
            "grade": grade,
            "context_length": eval_item["context_length"],
            "search_queries": eval_item["search_queries"],
        })

    # export eval results to a json file
    with open(f"/Users/zach/Code/KITE/results/{config_name}/eval_results_{test_set_name}.json", "w") as f:
        json.dump(eval_results, f, indent=4)

    # calculate average score
    total_score = 0
    for eval_item in eval_results:
        total_score += int(eval_item["grade"])
    avg_score = total_score / len(eval_results)
    print(f"Average score: {avg_score}")


#test_set_name = "ai_papers"
#test_set_name = "bvp_cloud"
#test_set_name = "sourcegraph"
test_set_name = "supreme_court_opinions"

#config_name = "top_k"
#config_name = "rse"
#config_name = "cch_top_k"
config_name = "cch_rse"

# load in the responses from a json file
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../responses'))
file_path = os.path.join(base_dir, f"{config_name}/{test_set_name}.json")
with open(file_path, "r") as f:
    eval_set = json.load(f)

# run the evaluation
run_evaluation(eval_set, test_set_name, config_name)
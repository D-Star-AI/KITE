import os
import sys
import json

# add ../../ to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../dsRAG')))

# import the necessary modules
from dsrag.knowledge_base import KnowledgeBase
from dsrag.auto_query import get_search_queries
from dsrag.llm import OpenAIChatAPI, AnthropicChatAPI


RESPONSE_SYSTEM_MESSAGE = """
You are a response generation system. Please generate a response to the user input based on the provided context. Your response should be as concise as possible while still fully answering the user's question.

Your response must ONLY be based on the provided context in the CONTEXT section below. Do not use any external information or knowledge. If the provided context is not sufficient to generate a response, you should indicate that you need more information.

CONTEXT
{context}
""".strip()

def get_response(question: str, context: str):
    #client = OpenAIChatAPI(model="gpt-4o-2024-08-06", temperature=0.0)
    client = AnthropicChatAPI(model="claude-3-5-sonnet-20240620", temperature=0.0)
    chat_messages = [{"role": "system", "content": RESPONSE_SYSTEM_MESSAGE.format(context=context)}, {"role": "user", "content": question}]
    return client.make_llm_call(chat_messages)

#test_set_name = "ai_papers"
#test_set_name = "bvp_cloud"
test_set_name = "sourcegraph"
#test_set_name = "supreme_court_opinions"

config_name = "top_k"
#config_name = "auto_query_top_k"
#config_name = "rse"
#config_name = "cch_top_k"
#config_name = "cch_rse"
#config_name = "auto_query_cch_top_k"
#config_name = "auto_query_cch_rse"

if "cch" in config_name:
    if test_set_name in ["ai_papers", "bvp_cloud"]:
        kb_id = f"KITE_{test_set_name}_w_CCH_GT" # had to re-run these and use generated titles
    else:
        kb_id = f"KITE_{test_set_name}_w_CCH"
else:
    kb_id = f"KITE_{test_set_name}_no_CCH"

if "auto_query" in config_name:
    use_auto_query = True
    top_k = 10
else:
    use_auto_query = False
    top_k = 20 # use a higher top_k since only one query is used

if "rse" in config_name:
    use_rse = True
else:
    use_rse = False

kb = KnowledgeBase(kb_id)

questions_file_path = f"/Users/zach/Code/KITE/queries/{test_set_name}.json"

with open(questions_file_path, "r") as f:
    eval_items = json.load(f)

unique_doc_ids = set()

for eval_item in eval_items:
    question = eval_item["query"]
    print(f"Question: {question}")

    if use_auto_query:
        search_queries = get_search_queries(question, max_queries=3)
    else:
        search_queries = [question]
        
    eval_item["search_queries"] = search_queries
    print(f"Search queries: {search_queries}")

    # get the context by running the search queries with either kb.search or kb.query
    if use_rse:
        relevant_segments = kb.query(search_queries)
        context = "\n\n".join([segment["text"] for segment in relevant_segments])
        
        doc_ids = [segment["doc_id"] for segment in relevant_segments]
        print (doc_ids)
        unique_doc_ids.update(doc_ids)
    else:
        all_search_results = []
        for query in search_queries:
            search_results = kb.search(query, top_k=top_k)
            all_search_results.extend(search_results)

        search_results = [result['metadata']['chunk_text'] for result in all_search_results] # get the text of the search results

        # deduplicate search results while maintaining order
        seen = set()
        deduped_search_results = [x for x in search_results if not (x in seen or seen.add(x))]
        context = "\n\n".join(deduped_search_results)

        doc_ids = [result['metadata']['doc_id'] for result in all_search_results]
        unique_doc_ids.update(doc_ids)
    
    eval_item["context_length"] = len(context)

    #response = get_response(question, context)
    #eval_item["response"] = response

    #print()
    #print(response)

print(f"Unique doc ids: {unique_doc_ids}")

# save the unique doc ids to a file
file_path = f"sourcegraph_unique_doc_ids_{config_name}.txt"
with open(file_path, "w") as f:
    for doc_id in unique_doc_ids:
        f.write(f"{doc_id}\n")

"""
output_file_path = f"/Users/zach/Code/KITE/responses/{config_name}/{test_set_name}.json"

with open(output_file_path, "w") as f:
    json.dump(eval_items, f, indent=4)
"""
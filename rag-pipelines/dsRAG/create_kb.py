import os
import sys
import time

# add ../../ to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# import the necessary modules
from dsrag.knowledge_base import KnowledgeBase
from dsrag.embedding import CohereEmbedding
from dsrag.reranker import CohereReranker
from dsrag.vector_db import ChromaDB
from dsrag.document_parsing import extract_text_from_pdf, extract_text_from_docx

auto_context_config = {
    "use_generated_title": True,
    "get_document_summary": True,
}

semantic_sectioning_config = {
    "use_semantic_sectioning": False
}
    
"""
kb_id = "KITE_ai_papers_w_CCH_GT"
title = "AI Papers"
description = "A collection of recent papers about AI."
directory = "/Users/zach/Code/KITE/knowledge-base-content/ai-papers"
"""


kb_id = "KITE_bvp_cloud_w_CCH_GT"
title = "BVP Cloud Index 10-Ks"
description = "A collection of 10-Ks from BVP Cloud Index companies."
directory = "/Users/zach/Code/KITE/knowledge-base-content/bvp-cloud-index-10k"


"""
kb_id = "KITE_sourcegraph_w_CCH"
title = "Sourcegraph company handbook"
description = "Company handbook for Sourcegraph, a company that provides code search and navigation tools."
directory = "/Users/zach/Code/KITE/knowledge-base-content/sourcegraph-company-handbook"
"""

"""
kb_id = "KITE_supreme_court_opinions_w_CCH"
title = "Supreme Court opinions 2023"
description = "All Supreme Court opinions from 2023."
directory = "/Users/zach/Code/KITE/knowledge-base-content/supreme-court-opinions-2023"
"""

kb = KnowledgeBase(
    kb_id=kb_id,
    title=title,
    description=description,
    embedding_model=CohereEmbedding(),
    reranker=CohereReranker(),
    vector_db=ChromaDB(kb_id=kb_id),
    exists_ok=False,
)

# add documents
for root, dirs, files in os.walk(directory):
    for file_name in files:
        if file_name.endswith(('.docx', '.md', '.txt', '.pdf')):
            try:
                file_path = os.path.join(root, file_name)
                clean_file_path = file_path.replace(directory, "")
                
                if file_name.endswith('.docx'):
                    text = extract_text_from_docx(file_path)
                elif file_name.endswith('.pdf'):
                    text = extract_text_from_pdf(file_path)
                elif file_name.endswith('.md') or file_name.endswith('.txt'):
                    with open(file_path, 'r') as f:
                        text = f.read()

                #document_title = clean_file_path # only use this config for the Sourcegraph dataset
                document_title = ""
                kb.add_document(doc_id=clean_file_path, text=text, document_title=document_title, auto_context_config=auto_context_config, semantic_sectioning_config=semantic_sectioning_config)
                time.sleep(1) # pause to avoid hitting API rate limits
            except:
                print (f"Error reading {file_name}")
                continue
        else:
            print (f"Unsupported file type: {file_name}")
            continue
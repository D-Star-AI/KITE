import os
import sys
import json
import numpy as np

# add ../../ to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def get_grades_for_one_test_set(config_name: str, test_set_name: str) -> list[int]:
    file_path = f"/Users/zach/Code/KITE/results/{config_name}/eval_results_{test_set_name}.json"
    with open(file_path, "r") as f:
        eval_results = json.load(f)

    grades = []
    for eval_result in eval_results:
        grades.append(int(eval_result["grade"]))

    return grades

#config_name = "top_k"
#config_name = "rse"
#config_name = "cch_top_k"
config_name = "cch_rse"

test_set_names = ["ai_papers", "bvp_cloud", "sourcegraph", "supreme_court_opinions"]

all_avg_grades = []
for test_set_name in test_set_names:
    grades = get_grades_for_one_test_set(config_name, test_set_name)
    avg_grade = sum(grades) / len(grades)
    all_avg_grades.append(avg_grade)
    print (f"Test set: {test_set_name}, avg grade: {np.round(avg_grade, 1)}")

overall_avg_grade = sum(all_avg_grades) / len(all_avg_grades)
print(f"\nOverall avg grade: {np.round(overall_avg_grade, 2)}")
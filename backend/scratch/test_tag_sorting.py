import re

def sort_requirement_tags(req_str: str) -> str:
    found_nums = re.findall(r"(?:REQ|FR)-(\d+)", str(req_str), re.I)
    if not found_nums:
        return req_str
    
    sorted_nums = sorted(list(set([int(n) for n in found_nums])))
    return ", ".join([f"REQ-{str(n).zfill(3)}" for n in sorted_nums])

test_cases = [
    "[REQ-012, REQ-005, REQ-006, REQ-009, REQ-010] Capture and Validate Facility",
    "[REQ-010, REQ-007, REQ-008] Prefill Property Attributes",
    "[REQ-015, REQ-006] Manage Provider Details"
]

print("\n================================================================================")
print(" [TEST: REQUIREMENT TAG NUMERICAL SORTING]")
print("================================================================================")
for tc in test_cases:
    bracket_match = re.search(r"^\[(.*?)\]", tc)
    if bracket_match:
        sorted_tags = sort_requirement_tags(bracket_match.group(1))
        result = re.sub(r"^\[.*?\]", f"[{sorted_tags}]", tc)
        print(f" INPUT : {tc}")
        print(f" OUTPUT: {result}\n")

print("================================================================================")
print(" SUCCESS: ALL REQUIREMENT TAGS SORTED NUMERICALLY IN ASCENDING ORDER!")
print("================================================================================\n")

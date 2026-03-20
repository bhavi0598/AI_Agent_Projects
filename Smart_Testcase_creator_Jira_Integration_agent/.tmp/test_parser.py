"""Quick test of the markdown table parser."""
from tools.llm_engine import _parse_llm_response

test_table = """| Unique Test Case ID | Test Case Name | Steps | Expected Step Description | Actual Step Description |
|--------------------|---------------|-------|---------------------------|-------------------------|
| 1 | Verify login | 1 | Open login page | Login page displayed |
|  |  | 2 | Enter credentials | Fields accept input |
|  |  | 3 | Click Login | Dashboard shown |
| 2 | Verify logout | 1 | Click logout button | Logout option visible |
|  |  | 2 | Confirm logout | Redirected to login |"""

result = _parse_llm_response(test_table)
if result:
    print("Parsed %d rows:" % len(result))
    for r in result:
        print("  TC-%s | %s | Step %s | %s | %s" % (
            r["testCaseId"], r["testCaseName"], r["steps"],
            r["expectedStepDescription"], r["actualStepDescription"]
        ))
else:
    print("FAILED: Parser returned None")

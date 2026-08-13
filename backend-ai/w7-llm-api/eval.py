import json
import httpx
from pathlib import Path
from colorama import init, Fore

init(autoreset=True)

# URL of the FastAPI endpoint
API_URL = "http://127.0.0.1:8000/enrich"

def load_cases():
    with open("evals/cases.json", "r") as f:
        return json.load(f)

def run_eval():
    cases = load_cases()
    correct_count = 0
    total = len(cases)
    failures = []

    print("Running evaluation against the LLM Enrichment API...\n")

    with httpx.Client(timeout=40.0) as client:
        for i, case in enumerate(cases):
            input_data = case["input"]
            expected = case["expected_category"]
            
            try:
                response = client.post(API_URL, json=input_data)
                
                if response.status_code == 200:
                    result = response.json()
                    actual = result["category"]
                    
                    if actual == expected:
                        print(f"Case {i+1}: {Fore.GREEN}PASS{Fore.RESET} (Expected: {expected}, Got: {actual})")
                        correct_count += 1
                    else:
                        print(f"Case {i+1}: {Fore.RED}FAIL{Fore.RESET} (Expected: {expected}, Got: {actual})")
                        failures.append({
                            "input": input_data,
                            "expected": expected,
                            "actual": actual,
                            "summary": result.get("summary"),
                            "quality_flags": result.get("quality_flags")
                        })
                else:
                    print(f"Case {i+1}: {Fore.RED}ERROR{Fore.RESET} (HTTP {response.status_code})")
                    failures.append({"input": input_data, "error": response.text})
            except Exception as e:
                print(f"Case {i+1}: {Fore.RED}EXCEPTION{Fore.RESET} ({e})")
                failures.append({"input": input_data, "error": str(e)})

    score = (correct_count / total) * 100
    print(f"\n--- Eval Results ---")
    print(f"Score: {correct_count}/{total} ({score:.1f}%)")
    
    if failures:
        print("\nFailures:")
        for fail in failures:
            print(json.dumps(fail, indent=2))

if __name__ == "__main__":
    run_eval()

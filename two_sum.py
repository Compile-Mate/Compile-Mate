from typing import List

def two_sum(nums: List[int], target: int) -> List[int]:
    lookup = {}
    for i, num in enumerate(nums):
        if target - num in lookup:
            return [lookup[target - num], i]
        lookup[num] = i
    return []

if __name__ == "__main__":
    import sys
    import json
    
    # Read input from stdin
    input_data = sys.stdin.read().strip()
    
    # Parse input
    try:
        # Input format: [2,7,11,15] 9
        nums_str, target_str = input_data.split('\n')
        nums = json.loads(nums_str)
        target = int(target_str)
        
        # Get result
        result = two_sum(nums, target)
        
        # Print result in required format
        print(json.dumps(result))
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1) 
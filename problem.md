# Two Sum

## Basic Information
- **Id**: 1
- **Name**: Two Sum
- **Type**: Array
- **Difficulty**: Easy
- **Time Limit**: O(n)
- **Space Complexity**: O(n)
- **Acceptance Rate**: Not specified

## Problem Description
Given an array of integers `nums` and an integer `target`, return the indices of the two numbers such that they add up to the target.

Each input will have exactly one solution, and you may not use the same element twice.

### Task
Find and return the two indices (`i` and `j`) such that `nums[i] + nums[j] == target`

### Parameters
- `nums`: List[int] - An array of integers
- `target`: int - The target sum to find

### Returns
- List[int] - A list containing two indices `[i, j]` where `nums[i] + nums[j] == target`

### Constraints
- 2 <= nums.length <= 10⁴
- -10⁹ <= nums[i] <= 10⁹
- Exactly one solution exists
- You may not use the same element twice

## Examples
### Example 1
```
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 2 + 7 == 9
```

### Example 2
```
Input: nums = [3,2,4], target = 6
Output: [1,2]
Explanation: Because nums[1] + nums[2] == 2 + 4 == 6
```

### Example 3
```
Input: nums = [3,3], target = 6
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 3 + 3 == 6
```

## Function Templates

### Python
```python
from typing import List

def two_sum(nums: List[int], target: int) -> List[int]:
    # write your code here
    pass
```

### C++
```cpp
#include <vector>
#include <unordered_map>
using namespace std;

vector<int> two_sum(vector<int>& nums, int target) {
    // write your code here
}
```

### Java
```java
import java.util.*;

public class Solution {
    public int[] two_sum(int[] nums, int target) {
        // write your code here
    }
}
```

## Solutions

### Approach 1: Hash Table
**Time Complexity**: O(n)  
**Space Complexity**: O(n)  
**Strategy**: Use a hash table to store the complement of each number.

#### Python Solution
```python
from typing import List

def two_sum(nums: List[int], target: int) -> List[int]:
    lookup = {}
    for i, num in enumerate(nums):
        if target - num in lookup:
            return [lookup[target - num], i]
        lookup[num] = i
```

#### C++ Solution
```cpp
vector<int> two_sum(vector<int>& nums, int target) {
    unordered_map<int, int> lookup;
    for (int i = 0; i < nums.size(); ++i) {
        if (lookup.count(target - nums[i])) {
            return {lookup[target - nums[i]], i};
        }
        lookup[nums[i]] = i;
    }
    return {};
}
```

#### Java Solution
```java
public int[] two_sum(int[] nums, int target) {
    Map<Integer, Integer> lookup = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        if (lookup.containsKey(target - nums[i])) {
            return new int[]{lookup.get(target - nums[i]), i};
        }
        lookup.put(nums[i], i);
    }
    return new int[]{};
}
```

## Notes
- The solution uses a hash table for O(n) time complexity
- Each input has exactly one solution
- The same element cannot be used twice
- The order of returned indices doesn't matter 
#include<vector>
#include<unordered_map>
using namespace std;

class Solution {
    public:
    unordered_map<int,int>hashtable;
    vector<int> twoSum(vector<int>& nums, int target) 
    {
        for(int i=0;i<nums.size();i++)
        {
            int key=target-nums[i];
            if(hashtable.find(key)==hashtable.end())
            {
                hashtable[nums[i]]=i;
            }
            else
            {
                return vector{i,hashtable[key]};
            }
        }
        return vector{0};
    }
};
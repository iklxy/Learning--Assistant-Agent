#include<vector>
using namespace std;

//dp

class Solution {
    public:
        int maxSubArray(vector<int>& nums) 
        {
            int k=nums.size();
            int dp[k];
            int Count=0;

            int Max=nums[0];

            dp[0]=nums[0];

            for(int i=1;i<k;i++)
            {
                if(dp[i-1]>0)
                {
                    dp[i]=dp[i-1]+nums[i];
                }
                else
                {
                    dp[i]=nums[i];
                }
                Max=max(Max,dp[i]);
            }
            return Max;
        }
};
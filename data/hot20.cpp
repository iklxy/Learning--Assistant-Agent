#include<vector>
using namespace std;

class Solution {
    public:
        int lengthOfLIS(vector<int>& nums) 
        {
            vector<int>dp(nums.size(),0);

            dp[0]=1;
            int MaxL=dp[0];
            for(int i=1;i<nums.size();i++)
            {
                int Max=0;
                for(int j=0;j<i;j++)
                {
                    if(nums[j]<nums[i])
                    {
                        Max=max(Max,dp[j]);
                    }
                }
                dp[i]=Max+1;
                MaxL=max(dp[i],MaxL);
            }
            return MaxL;
        }
};
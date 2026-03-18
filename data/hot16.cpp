//小偷打劫
//算法思路：dp，每次走到第i个房子，有两个选择，1：偷这间房子，然后加上前[i-2]个房子的钱 2:不偷，保持前[i-1]个房子的钱
#include<vector>
using namespace std;

class Solution {
    public:
        int rob(vector<int>& nums) 
        {
            vector<int>dp(nums.size(),0);

            for(int i=0;i<nums.size();i++)
            {
                if(i==0)
                {
                    dp[0]=nums[0];
                }
                else if(i==1)
                {
                    dp[1]=max(dp[0],nums[1]);
                }
                else
                {
                    dp[i]=max(dp[i-1],nums[i]+dp[i-2]);
                }
            }
            return dp[nums.size()-1];
        }
};
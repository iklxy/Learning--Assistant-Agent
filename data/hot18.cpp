//零钱兑换问题
#include<vector>
using namespace std;

class Solution {
    public:
        int coinChange(vector<int>& coins, int amount) 
        {
            vector<int>dp(amount+1,INT_MAX);
            dp[0]=0;

            for(int i=1;i<=amount;i++)
            {
                for(int &x:coins)
                {
                    if(i-x>=0)
                    {
                        if(dp[i-x]!=INT_MAX)
                        {
                            dp[i]=min(dp[i],dp[i-x]+1);
                        }
                    }
                }
            }
            return dp[amount]==INT_MAX ? -1 :dp[amount];
        }
};
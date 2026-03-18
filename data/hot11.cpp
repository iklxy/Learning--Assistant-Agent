//滑动窗口最大值
#include<vector>
#include<queue>
using namespace std;

class Solution {
    public:
        vector<int> maxSlidingWindow(vector<int>& nums, int k) 
        {
            priority_queue<pair<int,int> > q;

            vector<int>answer;

            for(int i=0;i<nums.size();i++)
            {
                q.push({nums[i],i});

                while(q.top().second<=i-k)
                {
                    q.pop();
                }

                if(i>=k-1)
                {
                    answer.push_back(q.top().first);
                }
            }
            return answer;
        }
};
#include<vector>
using namespace std;


class Solution {
    public:
        vector<vector<int>> generate(int numRows) 
        {
            vector<vector<int>>answer;

            if(numRows>=1)
            {
                answer.push_back(vector<int>{1});
            }
            if(numRows>=2)
            {
                answer.push_back(vector<int>{1,1});
            }
            if(numRows>2)
            {
                for(int i=2;i<numRows;i++)
                {
                    vector<int>temp=answer[i-1];
    
                    vector<int>ans_;
                    for(int j=0;j<i+1;j++)
                    {
                        if(j==0 || j==i)
                        {
                            ans_.push_back(1);
                        }
                        else
                        {
                            ans_.push_back(temp[j]+temp[j-1]);
                        }
                    }
                    answer.push_back(ans_);
                }
            }
            return answer;
        }
};
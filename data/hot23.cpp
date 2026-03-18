//最长有效括号
#include<string>
#include<stack>
using namespace std;

class Solution {
    public:
        int longestValidParentheses(string s) 
        {
            stack<int>S;

            S.push(-1);
            int maxL=0;

            for(int i=0;i<s.length();i++)
            {
                if(s[i]=='(')
                {
                    S.push(i);
                }
                else
                {
                    S.pop();
                    if(S.empty())
                    {
                        S.push(i);
                    }
                    else
                    {
                        int currentL=i-S.top();
                        maxL=max(maxL,currentL);
                    }
                }
            }
            return maxL;
        }
};
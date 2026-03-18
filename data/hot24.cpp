#include<string>
#include<cmath>
#include<algorithm>
#include<vector>
using namespace std;

struct ListNode 
{
         int val;
         ListNode *next;
         ListNode() : val(0), next(nullptr) {}
         ListNode(int x) : val(x), next(nullptr) {}
         ListNode(int x, ListNode *next) : val(x), next(next) {}
};

class Solution {
    public:
        bool isPalindrome(ListNode* head) 
        {
            vector<int>vals;

            ListNode* p=head;
            while(p!=nullptr)
            {
                vals.push_back(p->val);
                p=p->next;
            }
            int Left=0;
            int Right=vals.size()-1;

            while(Left<Right)
            {
                if(vals[Left]!=vals[Right])
                {
                    return false;
                }
                Left++;
                Right--;
            }
            return true;
        }
};
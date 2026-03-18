//想明白入环点怎么找，快慢指针相遇处不一定等于入环点，数学推导入环点的公式
#include<iostream>
using namespace std;

struct ListNode 
{
         int val;
         ListNode *next;
         ListNode(int x) : val(x), next(nullptr) {}
};

class Solution {
    public:
        ListNode *detectCycle(ListNode *head) 
        {
            ListNode* fast=head;
            ListNode* slow=head;

            while(fast!=nullptr && fast->next!=nullptr)
            {
                slow=slow->next;
                fast=fast->next->next;

                if(slow==fast)
                {
                    ListNode* index1=head;
                    ListNode* index2=slow;

                    while(index1!=index2)
                    {
                        index1=index1->next;
                        index2=index2->next;
                    }
                    return index1;
                }
            }
            return NULL;
        }
    };
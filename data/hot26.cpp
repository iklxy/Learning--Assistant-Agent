//两数之和
#include<iostream>
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
        ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) 
        {
            ListNode* Add=new ListNode(-1);
            ListNode* curr=Add;

            int carry=0;

            while(l1!=nullptr || l2!=nullptr || carry !=0)
            {
                int val1 = (l1==nullptr) ? 0 :l1->val;
                int val2 = (l2==nullptr) ? 0 :l2->val;

                int sum = val1+val2+carry;

                carry = sum/10;
                int digital=sum%10;

                ListNode* newNode = new ListNode(digital);
                curr->next=newNode;
                curr=newNode;

                if(l1!=nullptr)
                {
                    l1=l1->next;
                }
                if(l2!=nullptr)
                {
                    l2=l2->next;
                }
            }
            return Add->next;
        }
};

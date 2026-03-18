class Solution {
    public:
        ListNode* removeNthFromEnd(ListNode* head, int n) 
        {
            int L=0;
            ListNode* p=head;
            while(p!=nullptr)
            {
                L++;
                p=p->next;
            }
            int Length=L-n;
         
            ListNode* dummy = new ListNode(0,head);
    
            ListNode* curr = head;
            ListNode* prev = dummy;
            for(int i=0;i<Length;i++)
            {
                prev=curr;
                curr=curr->next;
            }
            prev->next=curr->next;
            delete curr;
            ListNode* newhead=dummy->next;
            delete dummy;
            return newhead;
        }
    };
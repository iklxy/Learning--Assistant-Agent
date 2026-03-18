#include<vector>
using namespace std;

class Solution {
    public:
        void moveZeroes(vector<int>& nums) 
        {
            int dest=0;

            for(int cur=0;cur<nums.size();cur++)
            {
                if(nums[cur]!=0)
                {
                    int temp=nums[cur];
                    nums[cur]=nums[dest];
                    nums[dest]=temp;

                    dest++;
                }
            }
        }
    };
#include<vector>
using namespace std;

class Solution {
    public:
        int maxProduct(vector<int>& nums) 
        {
            int iMax=nums[0];
            int iMin=nums[0];
            int Max=nums[0];

            for(int i=1;i<nums.size();i++)
            {
                if(nums[i]<0)
                {
                    swap(iMax,iMin);
                }

                iMax=max(nums[i],nums[i]*iMax);
                iMin=min(nums[i],nums[i]*iMin);

                Max=max(iMax,Max);
            }
            return Max;
        }
};
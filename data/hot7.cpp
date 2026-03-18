//接雨水
#include<vector>
using namespace std;

class Solution 
{
    public:
        int trap(vector<int>& height) 
        {
            int k=height.size();

            int Lptr=0;
            int Rptr=k-1;

            int LeftMaxHeight=0;
            int RightMaxHeight=0;

            int sum=0;

            while(Lptr<Rptr)
            {
                if(height[Lptr]<=height[Rptr])
                {
                    if(height[Lptr]>=LeftMaxHeight)
                    {
                        LeftMaxHeight=height[Lptr];
                    }
                    else
                    {
                        sum+=LeftMaxHeight-height[Lptr];
                    }
                    Lptr++;
                }
                else
                {
                    if(height[Rptr]>=RightMaxHeight)
                    {
                        RightMaxHeight=height[Rptr];
                    }
                    else
                    {
                        sum+=RightMaxHeight-height[Rptr];
                    }
                    Rptr--;
                }
            }
            return sum;
        }
};
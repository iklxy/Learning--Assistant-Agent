//盛最多水的容器
#include<vector>
using namespace std;

class Solution {
    public:
        int maxArea(vector<int>& height) 
        {
            //短板效应
            int left=0;
            int right=height.size()-1;

            int max=0;

            while(left!=right)
            {
                int min_height=0;
                int max_w=0;

                if(height[left] > height[right])
                {
                    min_height=height[right];
                    max_w=min_height*(right-left);
                    right--;
                }
                else
                {
                    min_height=height[left];
                    max_w=min_height*(right-left);
                    left++;
                }
                
                max=(max_w>max)?max_w:max;
            }
            return max;
        }
};
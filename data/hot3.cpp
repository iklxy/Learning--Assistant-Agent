#include<vector>
#include<unordered_map>
using namespace std;

class Solution {
    public:
    unordered_map<int,int>hashtable;
        int longestConsecutive(vector<int>& nums) 
        {
            int longest_length=0;

            for(int& i : nums)
            {
                hashtable[i]=i;
            }

            for(auto it = hashtable.begin();it!=hashtable.end();it++)
            {
                if(hashtable.find(it->second-1)==hashtable.end())
                {
                    int current_length=1;
                    int current_num=it->second;

                    while(hashtable.find(++current_num)!=hashtable.end())
                    {
                        current_length++;
                    }

                    longest_length=(longest_length>current_length)?longest_length : current_length;
                }
            }

            return longest_length;
        }
    };
//无重复字符的最长子串
#include<vector>
#include<string>
using namespace std;

class Solution {
    public:
        int lengthOfLongestSubstring(string s) 
        {
            if(s=="")
            {
                return 0;
            }
            string Table="";

            int Lptr=0;
            int Rptr=0;

            int size=0;

            while(Rptr<s.length())
            {
                char current=s[Rptr];

                while(Table.find(current)!=string::npos)
                {
                    Table.erase(0,1);
                    Lptr++;
                }

                Table.push_back(current);
                Rptr++;
                size =max(size,(int)Table.length());
            }
            return size;
        }
};
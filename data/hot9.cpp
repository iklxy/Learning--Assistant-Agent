//字母异位词
#include<vector>
#include<string>
#include<algorithm>
using namespace std;

class Solution {
    public:
        vector<int> findAnagrams(string s, string p) 
        {
            vector<int>answer;

            vector<int>pCounter(26,0);
            vector<int>windowsCounter(26,0);

            int Rptr=0;
            int Lptr=0;

            for(char& c : p)
            {
                pCounter[c-'a']++;
            }

            while(Rptr<s.length())
            {
                windowsCounter[s[Rptr]-'a']++;

                if(Rptr-Lptr+1>p.length())
                {
                    windowsCounter[s[Lptr]-'a']--;
                    Lptr++;
                }

                if(Rptr-Lptr+1==p.length())
                {
                    if(pCounter==windowsCounter)
                    {
                        answer.push_back(Lptr);
                    }
                }
                Rptr++;
            }
            return answer;
        }

};
//最小覆盖子串
#include<string>
#include<unordered_map>
using namespace std;

class Solution {
    public:
        string minWindow(string s, string t) 
        {
            string answer="";
            unordered_map<char,int>t_map;
            unordered_map<char,int>s_map;
            
            for(char& c : t)
            {
                t_map[c]++;
            }

            int Lptr=0;
            int Rptr=0;

            int valid=0;

            int minlen=INT_MAX;
            int start=0;

            while(Rptr<s.length())
            {
                char Rc=s[Rptr];
                if(t_map.count(Rc))
                {
                    s_map[Rc]++;
                    if(s_map[Rc]<=t_map[Rc])
                    {
                        valid++;
                    }
                }

                while(valid==t.length())
                {
                    if(Rptr-Lptr+1<minlen)
                    {
                        minlen=Rptr-Lptr+1;
                        start=Lptr;
                    }

                    char Lc=s[Lptr];

                    if(t_map.count(Lc))
                    {
                        s_map[Lc]--;
                        if(s_map[Lc]<t_map[Lc])
                        {
                            valid--;
                        }
                    }
                    Lptr++;
                }
                Rptr++;
            }
            return minlen==INT_MAX?"":s.substr(start,minlen);
        }
};
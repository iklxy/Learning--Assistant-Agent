#include<vector>
#include<unordered_map>
#include<algorithm>
using namespace std;

//排序哈希
class Solution {
    public:
    unordered_map<string,vector<string> >map;
        vector<vector<string>> groupAnagrams(vector<string>& strs) 
        {
            for(string& s : strs)
            {
                string key=s;

                sort(key.begin(),key.end());
                map[key].push_back(s);
            }

            vector<vector<string> >answer;
            for(auto it=map.begin();it!=map.end();it++)
            {
                answer.push_back(it->second);
            }

            return answer;
        }
    };
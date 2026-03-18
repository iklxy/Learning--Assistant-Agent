#include<iostream>

int findsqartn(int n)
{
    int left = 1;
    int right = n;

    int ans = 0;
    while(left <= right)
    {
        int mid = (left + right)/2;
        if((mid*mid) <= n)
        {
            ans = mid;
            left = mid + 1;
        }
        else
        {
            right = mid - 1;
        }
    }
    return ans;
}

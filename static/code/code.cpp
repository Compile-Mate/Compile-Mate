#include<bits/stdc++.h>

using namespace std;

Write your Code Here.
int main(){
    
    int size;
    cin>>size;
    int * arr = new int[size];

    for(int i = 0;i<size;i++){
        cin>>arr[i];
    }

    cout<<solve(arr,size);

}
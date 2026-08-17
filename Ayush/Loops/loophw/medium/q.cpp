#include<iostream>
using namespace std;

int main(){
    int n =4;
    
    // for (int i = 1;i<=n;i++){ //row
    //     for(int j = 1;j<=i;j++){//col
    //         if(j % 2 == 0 && i % 2 == 0)
    //         cout<<"*";
    //     }
    //     cout<<endl;
    // }
    //  for (int i = 1;i<=n;i++){ //row
    //     for(int j = 1;j<=i;j++){//col
    //         cout<<j;
    //     }
    //     cout<<endl;
    // }
    for (int i = 1;i<=n;i++){ //row
        for(int j = 1;j<=i;j++){//col
            cout<<j;
        }
        cout<<endl;
    }


    return 0;
}
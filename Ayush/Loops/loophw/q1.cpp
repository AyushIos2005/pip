#include <iostream>
#include<ctime>
#include<windows.h>
using namespace std;

int main(){
    float delay = 2000;
    while(true){
        cout<<"Hello World"<<endl;
        cout<<"Eat"<<endl;
        cout<<"Code"<<endl;
        cout<<"Sleep"<<endl;

        // this_thread :: sleep_for(chrono::milliseconds((int)(delay * 1000)));
        Sleep((int)delay);
        if(delay > 50)
        {
        delay *= 0.95;
        }
    }
}
    
// Complete the code
#include <stdio.h>
#include<string.h>

int main() {
    char str[] = "ChefSaysHi";
    int count = 0;
    int scount =0;
    printf("%s",str);
    for(int i = 0;i < strlen(str);i++){
        if(str[i] >= 'A' && str[i] <= 'Z'){
            count++;
        }
        else{
            scount++;
        }
    }
    printf("%d and %d",count,scount);
    return 0;
}

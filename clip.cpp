#include<windows.h>
#include<iostream>
#include<string>

int main(){
    if(!OpenClipboard(NULL)){
        return 1;
    }

    HANDLE data=GetClipboardData(CF_UNICODETEXT);
    if(data==NULL){
        CloseClipboard();
        return 1;
    }

    wchar_t* pText=(wchar_t*)GlobalLock(data);
    if(pText==NULL){
        CloseClipboard();
        return 1;
    }

    int len=WideCharToMultiByte(CP_UTF8,0,pText,wcslen(pText),NULL,0,NULL,NULL);
    if(len>0){
        std::string utf8(len,'\0');
        WideCharToMultiByte(CP_UTF8,0,pText,wcslen(pText),&utf8[0],len,NULL,NULL);
        std::cout<<utf8<<std::endl;
    }

    GlobalUnlock(data);
    CloseClipboard();
    return 0;
}

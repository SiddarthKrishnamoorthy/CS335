using System;
public class Program
{
    int x = 0;
    int GCD(int num1, int num2)
    {
        int Remainder;
 
        while (num2 != 0)
        {
            Remainder = num1 % num2;
            num1 = num2;
            num2 = Remainder;
        }
 
        return num1;
    }
 
     int Main()
    {
        x = 10;
        int x, y;
        x = 9;
        print(GCD(x, y));
    }
}

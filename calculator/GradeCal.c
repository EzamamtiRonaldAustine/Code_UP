#include <stdio.h>
int main() {
    int score;
    printf("Enter the numeric score: ");
    scanf("%d", &score); 
     if (score >= 0 && score <= 100) {
        char grade;
      if (score >= 90 && score <= 100) {
            grade = 'A';
        } else if (score >= 80 && score < 90) {
            grade = 'B';
        } else if (score >= 70 && score < 80) {
            grade = 'C';
        } else if (score >= 60 && score < 70) {
            grade = 'D';
        } else {
            grade = 'F';
        }
        printf("The letter grade is: %c\n", grade);
    } else {
      printf("Invalid score! Please enter a score between 0 and 100.\n");
    }
    return 0;
}

/* discrete-time (time-stepped) simulation model (even though it's deterministic). */
/* CHANGE: Commented out the above descriptive line to prevent syntax errors. */

/* Given a principal amount and an interest rate,    */
/* this program computes principal payments and      */
/* total interest paid for the duration of the loan. */
/* For each payment period, the program shows the    */
/* balance remaining at the end of that period,      */
/* as well as how much of each payment goes to       */
/* interest. Useful for figuring out payment         */
/* strategies and the cost of borrowing.             */

/* This version compounds interest semi-annually,    */
/* doing it according to the bank's formula. cw 8/92 */

/* This is sort of a time-stepped simulation, with   */
/* the steps being the payment interval. But it is   */
/* really just a direct calculation, with no use of  */
/* randomization at all. Extension to variable-rate  */
/* mortgages remains for future work!                */

#include <stdio.h>
#include <math.h>

/* If this flag is on, the program interactively asks you */
/* for the principal amount, the interest rate, payment   */
/* size, and payment frequency.                           */
/* Otherwise, you can hardcode values and get a printout. */
#define INTERACTIVE 1

#define MONTH_FUDGE 1 /* Hack month stuff */

float interest;
float taxes;
float amount;
float payment;

int main()
  {
    int i, j;
    float rate;
    float intamt;
    float inttotal;
    int paymentnum;
    int paymentsperyear;
    float intsemi;

    /* Daily interest factor, period interest factor.  */
    double dif, pif;
    /* annual interest rate, and compounding frequency */
    float a, f;
    int days;
    double x, y;

#ifdef INTERACTIVE
    printf(" Amount of loan? ");
    scanf("%f", &amount);

    printf("Annual interest rate? ");
    scanf("%f", &interest);

    printf("Payment interval? (in days) ");
    scanf("%d", &days);

    printf("Payment size? ");
    scanf("%f", &payment);

    printf("Taxes/Insurance per payment? ");
    scanf("%f", &taxes);
#else
    amount = 100000.0;
    interest = 10.5;
    payment = 250.00;
    taxes = 20.0;
    days = 7;
#endif
    paymentsperyear = (int) (0.3 + 1.0*365.0/days);

    /* Compute daily interest factor */
    f = 2;
    a = 0.01 * interest;
    x = 1 + a/f;
    y = f/365;
/*    printf("x = %e, y = %e\n", x, y); */

    dif = pow(x, y) - 1;
/*    printf("DIF = %e\n", dif); */

    x = 1.0 + dif;
    y = 1.0 * days;
/*    printf("x = %e, y = %e\n", x, y); */
    /* Logic: Compute the Daily Interest Factor (DIF) and Period Interest Factor (PIF) */
    /* using the bank's semi-annual compounding formula. PIF = (1 + a/f)^(f*days/365) - 1 */
    pif = pow(x, y) - 1;
/*    printf("PIF = %e\n", pif); */

    printf("\n\n         --- Mortgage Payment Summary ---\n\n");
    printf("Initial amount: $%4.2f\n", amount);
    printf("Annual interest rate: %5.3f%%\n", interest);
    printf("Payment size: $%6.2f\n", payment);
    printf("Payment period: every %d days\n\n", days);

    printf("Payment  Taxes Interest  PPLReduction  PPLBalance  TotalInterest\n");
    printf("-------------------------------------------------------------\n");
    inttotal = 0;
    paymentnum = 1;

    intsemi = 0;
    
    /* ================================================================= */
    /* BUG FIX: Infinite loop guard                                       */
    /* If (payment - taxes) <= first period interest, the balance will    */
    /* never decrease. The loan can never be paid off. Warn and exit.     */
    /* Without this check the while(amount > 0) loop runs forever.       */
    /* ================================================================= */
    if( (payment - taxes) <= (amount * pif) )
      {
        printf("\nERROR: Payment cannot cover interest!\n");
        printf("  Net payment (payment - taxes) = $%.2f\n", payment - taxes);
        printf("  First period interest          = $%.2f\n", amount * pif);
        printf("  The loan balance will grow, not shrink.\n");
        printf("  Increase your payment or reduce taxes/insurance.\n");
        return 1;
      }

    while( amount > 0 )
      {
	/* Simulation Step: Incrementally update balance and interest for each period */
	intamt = amount * pif; /* Interest for this period */
	amount = amount + intamt - (payment - taxes); /* Update principal balance */
	inttotal += intamt; /* Accumulate total interest */
	printf("  %2d  %5.2f %8.2f   %6.2f      %10.2f      %10.2f\n",
	       paymentnum, taxes, intamt, payment - taxes - intamt, amount, inttotal);
	if( paymentnum % paymentsperyear == 0 )
	  {
	    printf("   ------------  End of year %d ----------- \n",
		   paymentnum/paymentsperyear);
	    /* This prints a form feed character to get to next page */
	    if( paymentsperyear > 50 )
	      printf("\n");
	    printf("\n\nPayment  Interest  PPL Reduction  PPL Balance  Total Interest\n");
	    printf("-------------------------------------------------------------\n");
	  }
	paymentnum++;
#ifdef MONTH_FUDGE
	/* Kludge to approximate a year better for monthly payments */
	if( days == 30 )
	  days = 31;
	else if( days == 31 )
	  days = 30;
	/* Recompute pif */
	x = 1.0 + dif;
	y = 1.0 * days;
	pif = pow(x, y) - 1;
#endif
	}
    printf("Total interest paid: %10.2f\n", inttotal);
  }

# A Cool Tool for Simulating Insurance Claims

## 1. What's This All About?

Hey there, I’m Matt! This project is a simple but powerful model that simulates insurance claims for a few different types of policies. It's built on a classic idea in the insurance world called the "frequency-severity" method.

Here's the breakdown:

* **How often do claims happen? (Frequency)**: We use a **Poisson distribution** to guess how many claims might pop up in a given year. It's a go-to method for modeling random events.
* **How big are the claims? (Severity)**: For the size of each claim, we use a **Lognormal distribution**. This is a great fit because it reflects reality: most claims are small, but every once in a while, a really big one can happen.

The model runs a simulation for 10,000 years to get a good look at all the possible outcomes. It then spits out some key stats that insurance pros use all the time: **Expected Loss**, **Value at Risk (VaR)**, and **Tail Value at Risk (TVaR)**. These numbers are super important for figuring out how to price policies and manage risk.

Everything gets neatly exported to an Excel file so you can dig in and play with the data.

## 2. How to Get It Running

Ready to try it out? It's pretty straightforward.

1.  **Get the Right Stuff**: First, make sure you have Python and a few essential libraries. Just open your terminal and run this command:
    ```bash
    py -m pip install pandas numpy scipy openpyxl
    ```
2.  **Run the Script**: Save the code as a Python file (like `claims-sim.py`). Then, in the same terminal, run:
    ```bash
    py claims-sim.py
    ```
3.  **Check the Output**: You'll find a new Excel file called `claims_simulation_results.xlsx` in the same folder. It has two tabs:
    * `Simulated Annual Losses`: All the raw data from the 10,000-year simulation.
    * `Risk Metrics Summary`: A neat table with all the important stats calculated for you.

## 3. A Peek Under the Hood: The Code Explained

Curious about how the script actually works? Here’s a simple tour.

The code is split into a few main parts:

* **`simulate_claims` function**: This is the engine of the whole operation. For each type of insurance (like Auto or Property), it:
    1.  **Rolls the dice for claim counts**: It uses `np.random.poisson()` to simulate the number of claims for each of the 10,000 years.
    2.  **Generates claim sizes**: It then creates a random size for every single claim using `np.random.lognormal()`.
    3.  **Applies the rules**: It subtracts the deductible and applies the policy limit to each claim to figure out how much the insurer actually has to pay.
    4.  **Adds it all up**: Finally, it sums up all the paid claims for each year to get the total annual loss.
* **`calculate_risk_metrics` function**: This function takes the 10,000 years of simulated losses and does the number crunching. It calculates the average loss (Expected Loss) and finds the cutoff points for the worst-case scenarios (VaR and TVaR).
* **The Main Block (`if __name__ == '__main__':`)**: This is the part that kicks everything off.
    1.  It sets up all the parameters: how many years to simulate, the frequency/severity stats for each insurance line, and the deductible/limit.
    2.  It calls the `simulate_claims` function to run the simulation.
    3.  It then calls the `calculate_risk_metrics` function to get the summary stats.
    4.  Finally, it neatly packages everything into a pandas DataFrame and saves it as the `claims_simulation_results.xlsx` file.

## 4. Making Sense of the Results

The whole point of this is to see how different factors can shake up an insurance company's risk. The Excel file is your playground for this.

### What Happens if Frequency or Severity Changes?

If you tweak the assumptions, the risk numbers will change.

* **More Frequent Claims (`freq`)**:
    * **What it means**: More claims happening each year, on average.
    * **What happens to the stats**:
        * **Expected Loss**: Goes up. No surprise there.
        * **VaR/TVaR**: Goes up by even more. More claims mean a higher chance of a really bad year with tons of losses.
* **Bigger Claims (`sev_mean` or `sev_std`)**:
    * **What it means**: The average claim size gets bigger, or there's more wild variation in claim sizes (which means more potential for monster claims).
    * **What happens to the stats**:
        * **Expected Loss**: Goes up.
        * **VaR/TVaR**: Shoots up, especially when you increase the variation (`sev_std`). Those huge, unexpected claims are what really drive the risk of a catastrophic year.

### What About Deductibles and Limits?

These are the levers insurers use to control their risk.

* **A Higher Deductible**:
    * **What it means**: The customer pays for a bigger chunk of the small claims.
    * **What happens to the stats**:
        * **Expected Loss**: Drops, since all those little claims are no longer the insurer's problem.
        * **VaR/TVaR**: Also drops, but not as dramatically. The biggest, scariest claims will still be way over the deductible.
* **A Lower Limit**:
    * **What it means**: The insurer puts a cap on how much they'll pay for any single claim.
    * **What happens to the stats**:
        * **Expected Loss**: Dips a little, since only the biggest claims get trimmed.
        * **VaR/TVaR**: Drops a lot! Capping the huge claims is one of the best ways to protect against a financial disaster.

## 5. So, What's the Point?

This model is a great way to see actuarial science in action. By changing the inputs, you can see exactly how it affects the numbers that matter. This is the kind of analysis that helps insurance companies make smart decisions about:

* **Pricing**: The "Expected Loss" is basically the starting point for what a policy should cost.
* **Risk Management**: VaR and TVaR tell you how bad things could get, which is critical for planning and making sure you have enough cash on hand for a worst-case scenario.
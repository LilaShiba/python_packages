import random
import matplotlib.pyplot as plt

def monte_carlo_dice_sim(num_trials=100_000):
    one_die_results = []
    four_dice_results = []

    for _ in range(num_trials):
        # Roll one 4-sided die four times individually
        total = 0
        for _ in range(0, 4):
            total += random.randint(1,4)
        one_die_results.append(total)
        
        # Roll four 4-sided dice and sum them
        four_dice_sum = sum(random.randint(1, 4) for _ in range(4))
        four_dice_results.append(four_dice_sum)

    return one_die_results, four_dice_results

# Run simulation
one_die, four_dice = monte_carlo_dice_sim()

# Plot results
plt.figure(figsize=(10, 6))
plt.hist(one_die, bins=range(1, 6), alpha=0.6, label='One Die (x4)', edgecolor='black', align='left')
plt.hist(four_dice, bins=range(4, 17), alpha=0.6, label='Sum of Four Dice', edgecolor='black', align='left')
plt.xlabel('Die Result or Sum', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.title('Monte Carlo Simulation: One Die (×4) vs Four-Dice Sum', fontsize=14)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig("monte_carlo_dice_simulation.png")
plt.show()

#!/bin/bash
# calculator.sh
# Description: Performs basic arithmetic operations on two user-provided integers.
# Usage: ./calculator.sh


# Prompt for input
read -p "Enter first number: " num1
read -p "Enter second number: " num2

# Validate numeric input
if ! [[ "$num1" =~ ^-?[0-9]+$ && "$num2" =~ ^-?[0-9]+$ ]]; then
    echo "Error: Please enter valid integers."
    exit 1
fi

# Perform calculations
sum=$((num1 + num2))
diff=$((num1 - num2))
prod=$((num1 * num2))

# Handle division by zero
if [ "$num2" -eq 0 ]; then
    div="undefined (division by zero)"
else
    div=$((num1 / num2))
fi

# Display results
echo ""
echo "Results:"
echo "$num1 + $num2 = $sum"
echo "$num1 - $num2 = $diff"
echo "$num1 × $num2 = $prod"
echo "$num1 ÷ $num2 = $div"



